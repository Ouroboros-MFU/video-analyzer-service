from prometheus_client import Counter, Histogram

# сколько видео успешно обработано
videos_processed_total = Counter(
    "videos_processed_total",
    "Total number of successfully processed videos",
)

# сколько ошибок при обработке
videos_processing_errors_total = Counter(
    "videos_processing_errors_total",
    "Total number of errors during video processing",
)

# время обработки видео
videos_processing_time_seconds = Histogram(
    "videos_processing_time_seconds",
    "Time spent processing a video in seconds",
    buckets=(0.5, 1, 2, 5, 10, 30, 60, 120) 
)
