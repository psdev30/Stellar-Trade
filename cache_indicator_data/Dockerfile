FROM public.ecr.aws/lambda/python:3.9

COPY cache_indicator_data.py ${LAMBDA_TASK_ROOT}/

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --upgrade pip && \
    pip install -r ${LAMBDA_TASK_ROOT}/requirements.txt

CMD ["cache_indicator_data.lambda_handler"]
