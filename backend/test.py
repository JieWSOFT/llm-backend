import jwt


token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzQ5NDE4MjksInN1YiI6Im9LQTBRMFVmNDEzSEUwSTF3c2FRamhhbGY2ajAifQ.sRaB0BJ4syaDzcBt8RnUNvv_BL7V_uxfJqZzEtWoLz0'
secret = "W6MI8ra9_kAZdA3vAq_vdotE85sJbTCK261Gi5K8AFE"

payload = jwt.decode(
            token, secret,"HS256"
        )