"""ServiceNow incident integration for EDWEMP_API automation alerts."""

import json
import os
import sys
import threading
import traceback

SERVICE_NOW_ALERTS_ENABLED = True


def install_exception_hooks():
    """Create a ServiceNow incident for unhandled script and thread failures."""
    if getattr(sys, "_servicenow_exception_hooks_installed", False):
        return
    sys._servicenow_exception_hooks_installed = True
    default_sys_hook = sys.excepthook

    def report(exception_type, exception, exception_traceback, context):
        script_name = os.path.basename(sys.argv[0])
        message = "{}: {}".format(exception_type.__name__, exception)
        description = (
            "Script: {}\nContext: {}\nException type: {}\nError: {}\n\n"
            "Traceback:\n{}"
        ).format(
            script_name,
            context,
            exception_type.__name__,
            exception,
            "".join(
                traceback.format_exception(
                    exception_type, exception, exception_traceback
                )
            ),
        )
        try:
            create_failure_alert(message, description, {"File Name": script_name})
        except Exception as alert_error:
            sys.__stderr__.write(
                "ServiceNow incident creation failed while reporting {}: {}\n"
                .format(message, alert_error)
            )

    def sys_hook(exception_type, exception, exception_traceback):
        report(exception_type, exception, exception_traceback, "main thread")
        default_sys_hook(exception_type, exception, exception_traceback)

    sys.excepthook = sys_hook

    if hasattr(threading, "excepthook"):
        default_thread_hook = threading.excepthook

        def thread_hook(args):
            thread_name = getattr(args.thread, "name", "unknown")
            report(
                args.exc_type,
                args.exc_value,
                args.exc_traceback,
                "thread {}".format(thread_name),
            )
            default_thread_hook(args)

        threading.excepthook = thread_hook

    default_unraisable_hook = sys.unraisablehook

    def unraisable_hook(args):
        report(
            args.exc_type,
            args.exc_value,
            args.exc_traceback,
            "unraisable exception: {}".format(args.err_msg or "unknown context"),
        )
        default_unraisable_hook(args)

    sys.unraisablehook = unraisable_hook


class ServiceNowAlerts:
    """Create ServiceNow incidents for automation alerts."""

    def __init__(self):
        if not SERVICE_NOW_ALERTS_ENABLED:
            return

        import requests
        from requests.auth import HTTPBasicAuth
        from secret_key import (
            SERVICENOW_CLIENT_ID,
            SERVICENOW_CLIENT_SECRET,
            SERVICENOW_INSTANCE_URL,
        )

        self._requests = requests
        self._http_basic_auth = HTTPBasicAuth
        self._client_id = SERVICENOW_CLIENT_ID
        self._client_secret = SERVICENOW_CLIENT_SECRET
        self.instance_url = SERVICENOW_INSTANCE_URL.rstrip("/")
        if not self.instance_url.startswith("https://"):
            raise ValueError(
                "Set SERVICENOW_INSTANCE_URL in secret_key.py to your HTTPS "
                "ServiceNow instance URL."
            )
        if not self._client_id:
            raise ValueError("Set SERVICENOW_CLIENT_ID in secret_key.py.")
        if not self._client_secret:
            raise ValueError("Set SERVICENOW_CLIENT_SECRET in secret_key.py.")

    def create_incident(self, message, description, details=None):
        """Create and return an incident."""
        if not SERVICE_NOW_ALERTS_ENABLED:
            print("[ServiceNow] Test run: incident suppressed: {}".format(message))
            return None

        details = details or {}
        alert_key = "{}_{}".format(
            message, json.dumps(details, sort_keys=True, default=str)
        )

        response = self._requests.post(
            self.instance_url,
            json={
                "caller_id": "Srija Gatla",
                "category": "Application",
                "subcategory": "Monitoring",
                "channel": "Integration",
                "cmdb_ci": "EDWP",
                "short_description": alert_key[:160],
                "assignment_group": "EDWEMP",
                "priority": "3",
                "u_environment": "Prod",
                "u_monitored_item": message,
                "u_caused_by_change": details.get("u_caused_by_change", "No"),
                "u_caused_by": details.get("u_caused_by", "Automation"),
                "description": description,
            },
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            auth=self._http_basic_auth(self._client_id, self._client_secret),
            timeout=30,
        )
        response.raise_for_status()
        if response.status_code not in (200, 201):
            raise RuntimeError(
                "ServiceNow returned unexpected status {} while creating "
                "an incident.".format(response.status_code)
            )
        return response.status_code


def create_failure_alert(message, description, details=None):
    """Create a ServiceNow incident for an automation failure."""
    return ServiceNowAlerts().create_incident(message, description, details)
