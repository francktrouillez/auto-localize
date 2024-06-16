FROM python:3.12-slim

# Set the working directory
WORKDIR /action/workspace

# Copy the script into the container
COPY requirements.txt /action/workspace/requirements.txt
COPY src/ /action/workspace/src/
COPY entrypoint.sh /action/workspace/entrypoint.sh

# Install any dependencies (if required)
RUN python3 -m pip install --no-cache-dir -r /action/workspace/requirements.txt

ENTRYPOINT ["/action/workspace/entrypoint.sh"]
