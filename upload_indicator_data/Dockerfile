FROM public.ecr.aws/lambda/python:3.9

COPY indicator_data.py ${LAMBDA_TASK_ROOT}/
COPY sentiment_analysis.py ${LAMBDA_TASK_ROOT}/
COPY finance_sentiment.keras ${LAMBDA_TASK_ROOT}/

CMD ["indicator_data.lambda_handler"]

COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --upgrade pip && \
    pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

