from pathlib import Path
from platform import system
from os import environ, execve, getenv, pathsep
from sys import argv, stderr


def is_in_pyinstaller_context() -> bool:
    return bool(getenv("_PYI_ARCHIVE_FILE"))


def __pyi_ssl_certs_workaround() -> None:
    # Only run in Pyinstaller context
    if not is_in_pyinstaller_context():
        return

    if getenv('SSL_CERT_DIR') or getenv('SSL_CERT_FILE'):
        return

    ssl_files = (
        '/etc/ssl/certs/ca-certificates.crt',
        '/etc/pki/tls/certs/ca-bundle.crt',
        '/etc/ssl/ca-bundle.pem',
        '/etc/pki/tls/cacert.pem',
        '/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem',
        '/etc/ssl/cert.pem',
    )
    ssl_dirs = (
        '/etc/ssl/certs',
        '/etc/tls/pki/certs',
    )

    for file in ssl_files:
        if Path(file).exists():
            environ.update({'SSL_CERT_FILE': file})
            execve(argv[0], argv, environ)

    for dir in ssl_dirs:
        if Path(dir).exists():
            environ.update({'SSL_CERT_DIR': dir})
            execve(argv[0], argv, environ)

    print(
        '[~] Lookup SSL Cert failed: In case of SSL errors during HTTPS transaction '
        'set SSL_CERT_DIR or SSL_CERT_FILE env variable.',
        file=stderr
    )


def __find_7z_path() -> None:
    # Adding default 7-Zip path or user defined to PATH
    if getenv('LAUNCHER_WIN32_7Z_PATH'):
        environ['PATH'] += pathsep + getenv('LAUNCHER_WIN32_7Z_PATH')
        return

    default_install_path = (
        'C:\\Program Files\\7-Zip',
        'C:\\Program Files (x86)\\7-Zip',
    )

    for dir in default_install_path:
        if Path(dir).exists():
            environ['PATH'] += pathsep + dir
            break
    else:
        print(
            '[~] 7z default path not found. '
            'Set LAUNCHER_WIN32_7Z_PATH env variable to allow archive manipulation',
            file=stderr
        )


def __linux_bootstrap() -> None:
    __pyi_ssl_certs_workaround()


def __windows_bootstrap() -> None:
    __find_7z_path()


def __noop() -> None:
    pass


def bootstrap() -> None:
    {
        'Linux': __linux_bootstrap,
        'Windows': __windows_bootstrap,
    }.get(system(), __noop)()


bootstrap()
