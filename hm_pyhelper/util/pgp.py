"""Utility code to work with GPG signed messages."""


def get_payload_from_clearsigned_message(message: str) -> str:
    """
    Given a message in clearsign format removes signature and marker strings like
    -----BEGIN PGP SIGNATURE-----, -----BEGIN PGP SIGNED MESSAGE----- to extract
    the original payload.

    :param message: The message containing the signature and the payload.
    :return: Extracted payload as string. Calling code is responsible for
        converting it to proper data type.
    """
    lines = message.strip().split('\n')

    if len(lines) < 5 \
            or lines[0] != '-----BEGIN PGP SIGNED MESSAGE-----' \
            or lines[1].startswith('Hash:') is False:
        raise RuntimeError("Invalid message format, no --BEGIN PGP SIGNED MESSAGE-- header")

    start_idx = 3  # Payload starts from 3rd line in clearsigned messages
    end_idx = None

    for idx, line in enumerate(lines[3:]):
        if line.strip() == '-----BEGIN PGP SIGNATURE-----':
            end_idx = idx + start_idx
            break

    if end_idx is None:
        raise RuntimeError("Invalid message format, no --BEGIN PGP SIGNATURE-- section")

    return "\n".join(lines[start_idx: end_idx])
