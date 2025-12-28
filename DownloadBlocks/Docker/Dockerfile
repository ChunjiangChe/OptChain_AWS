# ------------------------------------------------------------------------------
# Stage 1: Builder
# ------------------------------------------------------------------------------
FROM rust:1.75 as builder

WORKDIR /usr/src/app

# create a new empty shell project
RUN cargo new --bin DownloadBlocks

# Switch to the project directory
WORKDIR /usr/src/app/DownloadBlocks

# Copy manifests from the PROJECT ROOT (relative to build context)
COPY Cargo.toml Cargo.lock ./

# Build dependencies only (caching layer)
RUN cargo build --release
RUN rm src/*.rs

# Copy source code from the PROJECT ROOT
COPY src ./src

# Build the actual application
# touch main.rs to ensure cargo rebuilds it
RUN touch src/main.rs && cargo build --release

# ------------------------------------------------------------------------------
# Stage 2: Runtime
# ------------------------------------------------------------------------------
FROM debian:bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy binary from builder
COPY --from=builder /usr/src/app/DownloadBlocks/target/release/DownloadBlocks /usr/local/bin/app

ENTRYPOINT ["app"]