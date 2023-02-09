#! /usr/bin/env python3
import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports(include=["pyfaidx", "pyhgvs"]):
    import pyhgvs
    import pyhgvs.utils as pyhgvs_utils
    import pyfaidx

fasta_error_tup = (pyfaidx.FastaIndexingError, pyfaidx.KeyFunctionError, pyfaidx.IndexNotFoundError, pyfaidx.VcfIndexNotFoundError,
                   pyfaidx.FastaNotFoundError, pyfaidx.FetchError, pyfaidx.BedError,
                   pyfaidx.RegionError, pyfaidx.UnsupportedCompressionFormat)

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    try:
        if fdp.ConsumeBool():
            with fdp.ConsumeMemoryFile(all_data=True, as_bytes=False) as ref_f:
                pyhgvs_utils.read_transcripts(ref_f)
        else:
            with fdp.ConsumeTemporaryFile('.fa', all_data=False, as_bytes=True) as fasta_name, pyfaidx.Fasta(fasta_name) as fa:
                pyhgvs.parse_hgvs_name(fdp.ConsumeRandomString(), fa)
    except pyhgvs.InvalidHGVSName:
        return -1
    except fasta_error_tup as e:
        return -1
    except (UnicodeDecodeError, NotImplementedError, RuntimeError):
        return -1
    except ValueError as e:
        if 'columns' in str(e) or 'literal' in str(e) or 'Duplicate key' in str(e):
            return -1
        raise
    except TypeError as e:
        if 'concatenate' in str(e):
            return -1
        raise


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
