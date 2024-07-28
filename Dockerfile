# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Add this before installing Python packages
RUN apt-get update && \
    apt-get install -y python3-tk && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install SpaCy and the English model
RUN pip install spacy && python -m spacy download en_core_web_sm

# Install xvfb; virtual display
RUN apt-get update && apt-get install -y xvfb

# Expose port 80 to the outside world
EXPOSE 80

# Run app.py when the container launches
CMD ["xvfb-run", "python", "OptimisticOptimizer.py"]

