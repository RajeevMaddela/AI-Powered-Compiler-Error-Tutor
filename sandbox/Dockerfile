# Lightweight sandbox image containing g++ and standard library only
FROM alpine:3.20

# Install g++ and standard C++ libraries, clean up cache immediately
RUN apk add --no-cache g++ libstdc++ musl-dev

# Create a restricted non-root user and group
RUN addgroup -g 10001 -S sandboxgroup && \
    adduser -u 10001 -S sandboxuser -G sandboxgroup -D

# Create execution workspace owned by non-root user
WORKDIR /workspace
RUN chown -R sandboxuser:sandboxgroup /workspace

# Switch to non-root user
USER sandboxuser

# Default command
CMD ["g++", "--version"]
