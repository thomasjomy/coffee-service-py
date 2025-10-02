    # Use the official MySQL base image
    FROM mysql:latest

    # Set environment variables for MySQL root password and database
    ENV MYSQL_ROOT_PASSWORD=password
    ENV MYSQL_DATABASE=coffees

    # Copy the init.sql file into the /docker-entrypoint-initdb.d directory
    # This directory is automatically processed by the MySQL container on first startup
    COPY init.sql /docker-entrypoint-initdb.d/
