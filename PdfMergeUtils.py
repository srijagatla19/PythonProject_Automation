import os
import tempfile
import traceback

from PyPDF2 import PdfReader

from AutomationLog import log_step


def write_merger_atomically(merger, output_path, component):
    log_step(component, f"START: prepare merged PDF {output_path}")
    output_dir = os.path.dirname(output_path)
    file_descriptor, temporary_path = tempfile.mkstemp(
        prefix=".emp-merge-", suffix=".pdf", dir=output_dir
    )
    os.close(file_descriptor)
    operation_error = None

    try:
        log_step(
            component,
            f"START: serialize merged PDF to temporary file {temporary_path}",
        )
        with open(temporary_path, "wb") as merged_stream:
            merger.write(merged_stream)
        log_step(
            component,
            f"END: PDF serialization finished; validate {temporary_path}",
        )
        with open(temporary_path, "rb") as merged_file:
            page_count = len(PdfReader(merged_file, strict=True).pages)
            if not page_count:
                raise ValueError("The merged PDF contains no pages.")
        log_step(component, f"END: PDF validation passed; pages={page_count}")
        log_step(component, f"START: replace final PDF with {temporary_path}")
        os.replace(temporary_path, output_path)
        log_step(component, f"END: final PDF created {output_path}")
    except BaseException as error:
        operation_error = error
        log_step(
            component,
            f"ERROR: merge failed for {output_path}: {type(error).__name__}: {error}\n"
            f"{traceback.format_exc()}",
        )
        raise
    finally:
        log_step(component, f"START: close merger for {output_path}")
        try:
            merger.close()
            log_step(component, f"END: close merger for {output_path}")
        except BaseException as cleanup_error:
            if operation_error is None:
                raise
            log_step(
                component,
                f"WARNING: failed to close merger after "
                f"{type(operation_error).__name__}: {cleanup_error}",
            )
        if os.path.exists(temporary_path):
            log_step(component, f"START: remove temporary PDF {temporary_path}")
            try:
                os.remove(temporary_path)
                log_step(component, f"END: removed temporary PDF {temporary_path}")
            except OSError as cleanup_error:
                if operation_error is None:
                    raise
                log_step(
                    component,
                    f"WARNING: could not remove temporary PDF {temporary_path}: "
                    f"{cleanup_error}. Original error remains "
                    f"{type(operation_error).__name__}.",
                )
