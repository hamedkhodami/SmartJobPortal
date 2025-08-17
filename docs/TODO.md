# TODO LIST

import urllib.parse

def get_redis_key(config, email):
    safe_email = urllib.parse.quote(email)
    return config['STORE_BY'].format(safe_email)

get_redis_key(LOGIN_OTP_CONFIG, 'user@example.com')
# خروجی: otp_auth_email_user%40example.com
---

# 🚩F1 Backend Core Development

### ✓ level 1 complete core
### ✓ level 2 complete account
### [] level 3 complete job
### [] level 4 complete notification
### [] level 5 complete dashboard
### [] level 6 complete public
### [] level 7 complete public
### [] level 8 complete public
### [] level 9 preparing for F2
