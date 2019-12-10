FROM alpine:3.10.2

RUN apk add --no-cache --update openssh-client

CMD ssh -v -o "StrictHostKeyChecking=no" -o "ExitOnForwardFailure=yes" -i /telegram_proxy.key -NT -L 0.0.0.0:1234:localhost:1234 telegram_proxy_host