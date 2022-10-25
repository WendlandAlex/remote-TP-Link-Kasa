def validate_totp(totp_object, mfa_code) -> bool:
    print(
        totp_object.now(), mfa_code, totp_object.verify(int(mfa_code))
    )
    return totp_object.verify(
        int(mfa_code)
        )