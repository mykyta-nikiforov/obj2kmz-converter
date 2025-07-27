#!/usr/bin/env python3

class ConverterScriptError(Exception):
    pass


class GeoreferencingError(ConverterScriptError):
    pass


class ModelConversionError(ConverterScriptError):
    pass


class FileProcessingError(ConverterScriptError):
    pass


class ValidationError(ConverterScriptError):
    pass
