FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    qpdf \
    tesseract-ocr \
    tesseract-ocr-eng \
    imagemagick \
    libmagickwand-dev \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

RUN sed -i '/<policy domain="coder" rights="none" pattern="PDF" \/>/d' /etc/ImageMagick-*/policy.xml || true

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

WORKDIR /workspace

FROM base AS development

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    vim \
    fonts-liberation \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    ruff \
    mypy \
    debugpy \
    ipython \
    types-Pillow

ENV PYTHONPATH=/workspace

CMD ["sleep", "infinity"]

FROM base AS production

COPY . . 

ENV PYTHONPATH=/workspace

ENTRYPOINT ["python"]
