import subprocess
import sys
import os


class KeyNotFound(Exception):
    pass


class KeyLibrary:
    def __init__(self, path):
        self._path = path
        self.keys_by_fingerprint = {}


    def _generate_public_key(self, fname):
        pkey_fname = fname + '.pub'
        if os.access(pkey_fname, os.R_OK):
            return
        print("public key does not exist for private key '%s'" % fname, file=sys.stderr)
        print("attemping to generate; you may be prompted for a passphrase.", file=sys.stderr)
        try:
            public_key = subprocess.check_output(['ssh-keygen', '-y', '-f', fname])
        except subprocess.CalledProcessError:
            return
        with open(pkey_fname, 'wb') as fd:
            fd.write(public_key)
        print("Generated public key successfully.", file=sys.stderr)
        return True

    def _scan_key(self, fname, recurse=False):
        try:
            output = subprocess.check_output(['ssh-keygen', '-l', '-f', fname])
        except subprocess.CalledProcessError:
            if not recurse and self._generate_public_key(fname):
                return self._scan_key(fname, recurse=True)

    def scan(self):
        skip = set(('config', 'known_hosts', 'authorized_keys'))
        for dirpath, dirnames, fnames in os.walk(self._path):
            for name, path in ((t, os.path.join(dirpath, t)) for t in fnames):
                if name.endswith('.pub'):
                    continue
                if name in skip:
                    continue
                self._scan_key(path)

    def lookup(self, fingerprint):
        try:
            return self.keys_by_fingerprint[fingerprint]
        except KeyError:
            raise KeyNotFound()