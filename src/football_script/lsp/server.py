from __future__ import annotations
from pygls.lsp.server import LanguageServer
from lsprotocol import types as lsp
from ..compiler.parser import parse_to_ast

class FsServer(LanguageServer):
    def __init__(self):
        super().__init__("football-script-ls", "0.1.0")

server = FsServer()

@server.feature(lsp.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: FsServer, params: lsp.DidOpenTextDocumentParams):
    _publish_diagnostics(ls, params.text_document.uri, params.text_document.text)

@server.feature(lsp.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: FsServer, params: lsp.DidChangeTextDocumentParams):
    text = params.content_changes[0].text if params.content_changes else ""
    _publish_diagnostics(ls, params.text_document.uri, text)

def _publish_diagnostics(ls: FsServer, uri: str, text: str):
    diags = []
    try:
        parse_to_ast(text, uri=uri)
    except Exception as e:
        rng = lsp.Range(start=lsp.Position(0, 0), end=lsp.Position(0, 1))
        diags.append(lsp.Diagnostic(range=rng, message=str(e), severity=lsp.DiagnosticSeverity.Error, source="parser"))
    ls.publish_diagnostics(uri, diags)

def run_server(host: str, port: int):
    server.start_tcp(host, port)
