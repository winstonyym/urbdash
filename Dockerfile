# Use the official miniconda3 base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /app

# Copy the environment.yml file into the container
COPY environment.yml .

# Create the Conda environment from the environment.yml file
RUN conda env create -f environment.yml

# Activate the environment
RUN echo "source activate $(head -1 environment.yml | cut -d' ' -f2)" > ~/.bashrc
ENV PATH /opt/conda/envs/$(head -1 environment.yml | cut -d' ' -f2)/bin:$PATH

# Copy your Dash application files into the container
COPY . .

# Expose the port your Dash application will run on
EXPOSE 8050

# Set the default command for the container, starting the Dash application
CMD ["python", "app.py"]