FROM openresty/openresty:alpine

# Create directory for error pages
RUN mkdir -p /usr/share/nginx/html

# Copy error pages
COPY html/403.html /usr/share/nginx/html/

# Copy nginx configuration
COPY nginx.conf /usr/local/openresty/nginx/conf/nginx.conf