# ===== Development Stage =====
FROM python:3.11-slim AS dev

WORKDIR /workspace

RUN apt-get update && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir \
    pandas \
    ipython \
    pytest \
    ruff

ENV MPLBACKEND=Agg

CMD ["sleep", "infinity"]

# ===== Production Stage =====
FROM python:3.11-slim AS prod

WORKDIR /workspace

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV MPLBACKEND=Agg

CMD ["python"]
