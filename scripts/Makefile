define HELPBODY
Available commands:

	make help                             - this thing

	make load_transfer                    - load send token API
	make load_get_balance                 - load read token API
	make load_batch_status                - load batch satus API
	make load_user_pub_keys               - load read user pub keys API
	make load_certificate_creation        - load certificate creation

endef

export HELPBODY

REST_API_URL=http://localhost:8080

CLIENTS=1
THREADS=1
TIME=30

help:
	@echo "$$HELPBODY"

load_transfer:
	wrk -c ${CLIENTS} -t ${THREADS} -d ${TIME} --latency -s ./token_post.lua ${REST_API_URL}/api/v1/token

load_get_balance:
	wrk -c ${CLIENTS} -t ${THREADS} -d ${TIME} --latency ${REST_API_URL}/api/v1/token/03fcc39066206a010d4a9b04ad3ebe6fbdcdd0ac8016973b005ede707322a9aa18

load_batch_status:
	wrk -c ${CLIENTS} -t ${THREADS} -d ${TIME} --latency ${REST_API_URL}/api/v1/batch_status/8620c54ed41eae6a61eef1374536abf0ea17ff7923d74bdae0b1f9a5b621b4042c085e62ea01260435a9769ab02d785f5088bf2873497ca38b128cb086cdcc1d

load_user_pub_keys:
	wrk -c ${CLIENTS} -t ${THREADS} -d ${TIME} --latency ${REST_API_URL}/api/v1/user/03fcc39066206a010d4a9b04ad3ebe6fbdcdd0ac8016973b005ede707322a9aa18/pub_keys

load_certificate_creation:
	wrk -c ${CLIENTS} -t ${THREADS} -d ${TIME} --latency -s ./certificate_put.lua ${REST_API_URL}/api/v1/certificate