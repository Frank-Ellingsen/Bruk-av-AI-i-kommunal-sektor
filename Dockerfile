FROM python:3.12-slim

WORKDIR /workspace

COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/workspace

CMD ["bash", "-lc", "python --version && python run_pipeline.py --help"]
