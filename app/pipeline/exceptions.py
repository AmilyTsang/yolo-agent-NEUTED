class PipelineException(Exception):
    def __init__(self, message: str, step: str = None):
        super().__init__(message)
        self.step = step
        self.message = message

class PreprocessingException(PipelineException):
    def __init__(self, message: str):
        super().__init__(message, step='preprocessing')

class DetectionException(PipelineException):
    def __init__(self, message: str):
        super().__init__(message, step='detection')

class VerificationException(PipelineException):
    def __init__(self, message: str):
        super().__init__(message, step='verification')

class FusionException(PipelineException):
    def __init__(self, message: str):
        super().__init__(message, step='fusion')

class DecisionException(PipelineException):
    def __init__(self, message: str):
        super().__init__(message, step='decision')

class ReportException(PipelineException):
    def __init__(self, message: str):
        super().__init__(message, step='report')