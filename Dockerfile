FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y gdal-bin libgdal-dev binutils
RUN pip install GDAL==3.2.2.1

# Install the requirements
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn 

# Copy the application files into the container
COPY . .

# Expose the port your Dash app will run on
EXPOSE 8050

# Run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8050", "app:server"]