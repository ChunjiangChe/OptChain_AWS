use clap::{Parser, Subcommand};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use std::sync::{
    atomic::{AtomicUsize, Ordering},
    Arc,
};
use std::time::Duration;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::time;

// --- Constants ---
const PAYLOAD_SIZE: usize = 25_730_432; // ~1.44 MB
const TEST_DURATION: u64 = 60; // Run test for 60 seconds

// Approximate size on wire: Payload + 8 bytes ID + 8 bytes Vec length
const STRUCT_WIRE_SIZE: usize = PAYLOAD_SIZE + 16; 

// --- CLI Argument Structure ---
#[derive(Parser)]
#[command(name = "P2P Bench")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Run as a Receiver Node (Server)
    Server {
        #[arg(short, long, default_value_t = 6042)]
        port: u16,
    },
    /// Run as the Sender Node (Client)
    Client {
        #[arg(required = true)]
        targets: Vec<String>,
    },
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct A {
    id: u64,
    data: Vec<u8>,
}

impl A {
    fn new(id: u64) -> Self {
        Self {
            id,
            data: vec![0u8; PAYLOAD_SIZE],
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cli = Cli::parse();
    match cli.command {
        Commands::Server { port } => run_server(port).await,
        Commands::Client { targets } => run_client(targets).await,
    }
}

// --- Server Logic (Receiver) ---
async fn run_server(port: u16) -> Result<(), Box<dyn std::error::Error>> {
    let addr = format!("0.0.0.0:{}", port);
    let listener = TcpListener::bind(&addr).await?;

    println!("=== RECEIVER MODE (Port {}) ===", port);
    
    // We just discard data as fast as possible to measure raw network capacity
    loop {
        if let Ok((mut socket, _)) = listener.accept().await {
            tokio::spawn(async move {
                let mut buf = vec![0u8; 64 * 1024]; 
                loop {
                    // Drain the socket
                    if socket.read(&mut buf).await.unwrap_or(0) == 0 {
                        break;
                    }
                }
            });
        }
    }
}

// --- Client Logic (Sender) ---
async fn run_client(targets: Vec<String>) -> Result<(), Box<dyn std::error::Error>> {
    println!("=== SENDER MODE ===");
    println!("Payload Size: {:.2} MB", PAYLOAD_SIZE as f64 / 1_024.0 / 1_024.0);
    println!("Target Nodes: {}", targets.len());
    println!("Duration:     {} seconds", TEST_DURATION);

    // 1. Prepare Target List
    struct TargetStats {
        addr: SocketAddr,
        counter: Arc<AtomicUsize>,
    }

    let mut target_stats = Vec::new();

    // Parse strings into socket addresses and create a counter for EACH
    for target in targets {
        if let Ok(addr) = target.parse::<SocketAddr>() {
            target_stats.push(TargetStats {
                addr,
                counter: Arc::new(AtomicUsize::new(0)),
            });
        } else {
            eprintln!("Invalid address skipped: {}", target);
        }
    }

    // 2. Spawn Connection Tasks
    for t_stat in &target_stats {
        let addr = t_stat.addr;
        let counter_ref = t_stat.counter.clone();
        
        tokio::spawn(async move {
            if let Ok(mut stream) = TcpStream::connect(addr).await {
                let a = A::new(1);
                let encoded_data = bincode::serialize(&a).unwrap();

                loop {
                    if stream.write_all(&encoded_data).await.is_err() {
                        break;
                    }
                    // Increment the counter SPECIFIC to this node
                    counter_ref.fetch_add(1, Ordering::Relaxed);
                }
            } else {
                eprintln!("Failed to connect to {}", addr);
            }
        });
    }

    println!("Benchmark running...");
    time::sleep(Duration::from_secs(TEST_DURATION)).await;

    // 3. Generate Report
    println!("\n{:<20} | {:<15} | {:<15}", "Node IP", "Total A Received", "Throughput (A/s)");
    println!("{:-<60}", "");

    let mut total_cluster_a = 0;

    for t_stat in &target_stats {
        let count = t_stat.counter.load(Ordering::Relaxed);
        let throughput = count as f64 / TEST_DURATION as f64;
        
        total_cluster_a += count;

        println!("{:<20} | {:<15} | {:<15.2}", 
            t_stat.addr.ip().to_string(), 
            count, 
            throughput
        );
    }

    println!("{:-<60}", "");
    println!("CLUSTER TOTAL: {} A", total_cluster_a);
    println!("Duration:      {} s", TEST_DURATION);

    std::process::exit(0);
}