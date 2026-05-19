FROM bashj79/kafka-kraft

WORKDIR /bin

COPY pre_start_kafka.sh pre_start_kafka.sh
COPY create_topics.sh create_topics.sh

RUN chmod u+x pre_start_kafka.sh

ENV KAFKA_ADVERTISED_LISTENERS="PLAINTEXT://kafka:9092"

WORKDIR /opt/kafka/bin

CMD [ "/bin/pre_start_kafka.sh" ]