# Stage 1: Build the Jaspr application
FROM dart:stable AS build
WORKDIR /app
COPY pubspec.* ./
RUN dart pub get
COPY . .
RUN dart pub global activate jaspr_cli
RUN export PATH="$PATH":"$HOME/.pub-cache/bin" && jaspr build -v

# Stage 2: Serve the pre-rendered static site with Nginx
# Jaspr in static mode produces only HTML/JS/CSS — no server binary
FROM nginx:alpine
# Copy the pre-rendered static output into Nginx's web root
COPY --from=build /app/build/jaspr/ /usr/share/nginx/html/
# Cloud Run injects PORT — Nginx default is 80, but Cloud Run expects 8080
# Replace the default Nginx config to listen on 8080
RUN printf 'server {\n\
    listen 8080;\n\
    server_name _;\n\
    root /usr/share/nginx/html;\n\
    index index.html;\n\
    # Serve pre-rendered routes cleanly\n\
    location / {\n\
        try_files $uri $uri/index.html =404;\n\
    }\n\
}\n' > /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
