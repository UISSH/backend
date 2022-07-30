import pathlib
import subprocess

from base.utils.format import format_completed_process
from base.utils.logger import plog
from website.applications.core.dataclass import BaseSSLCertificate


def issuing_certificate(instance) -> subprocess.CompletedProcess:
    valid = False
    plog.info(f'Issue a certificate for {instance.domain}')
    certificate_path = instance.ssl_config['path']['certificate']

    plog.debug(instance.ssl_config['path'])

    if certificate_path != '' and pathlib.Path(certificate_path).exists():

        try:
            cert = BaseSSLCertificate.get_certificate(certificate_path)
            plog.info(f"{instance.domain} cert info:\n{cert.__str__()}")
            if instance.domain not in cert.issued_common_name:
                valid = False
            elif instance.extra_domain is not None:
                valid = cert.valid()
                for domain in instance.extra_domain.split(","):
                    if domain not in cert.subject_alt_name:
                        valid = False
            else:
                valid = cert.valid()
        except:
            valid = False

    if valid:
        plog.info('Certificate is valid skip generating.')
        return subprocess.run("echo 'Certificate is valid skip generating.'", capture_output=True, shell=True)

    key_path = instance.ssl_config['path']['key']
    certificate_path = instance.ssl_config['path']['certificate']

    plog.info('Run certbot Issue certificate')
    cmd = ['certbot', 'certonly', '-n', '--nginx', '--reuse-key',
           '--agree-tos', '-m', instance.user.email,
           '--fullchain-path', certificate_path,
           '--key-path', key_path,
           '-d', instance.domain]

    if instance.extra_domain is not None and instance.extra_domain != '':
        extra_domain = instance.extra_domain.replace("\n", ",")
        for domain in extra_domain.split(","):
            cmd.append('-d')
            cmd.append(domain)
        cmd.append('--expand')

    # debug = True
    # if debug:
    #     plog.warning(
    #         "Note that the debug mode is turned on and the issued certificate will not actually take effect.")
    #     cmd.append('--dry-run')

    cmd.append('-v')

    p = subprocess.run(cmd, capture_output=True)
    msg = f"==============Issuing a certificate==================\n{' '.join(cmd)}\n"
    plog.info(msg)
    plog.info(f'{format_completed_process(p)}')
    return p
