"""User-related support functions for Internet Archive access."""

import ftplib
import socket

import exceptions

MAX_RETRY = 10

def validate(username, password):
    """Confirm that the username/password combination is valid; return True
    if valid, otherwise return False."""

    retry_count = 0

    while retry_count < MAX_RETRY:
        # attempt to open an FTP connection and log in
        try:
            server = ftplib.FTP('items-uploads.archive.org')
            server.login(username, password)

            # success; logout and return True
            server.quit()
            return True

        except ftplib.error_perm, e:
            # a login error occured
            return False
        
        except socket.error, e:
            # some socket error occured; increment the retry count
            retry_count = retry_count + 1
            continue

    # if we get this far we we're able to validate; raise an exception
    raise exceptions.CommunicationsException()
