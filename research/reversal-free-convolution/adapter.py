"""Keep bit-reversed frequency records inside the physical convolution caller.

Import only inside the authenticated physical-ring-product cohort. The private
Fourier object has a changed intermediate contract; expose the complete caller.
"""

from convolution_engine import Convolution
from fourier_engine import Fourier
from fourier_plan import FourierPlan
from words import need


class _FrequencyFourier(Fourier):
    """Forward returns B F_minus; opposite accepts B-ordered records."""

    def reversal(self, plan):
        need(isinstance(plan, FourierPlan), "compiled convolution frequency plan")
        need(self.current is not None, "live convolution frequency packet")
        # The same B cancels across both inputs and the record-local product.
        # Keep the inherited zero reversal count: no sparse router is invoked.


def convolution(layer):
    """Return the original natural-order convolution ABI with fewer routers."""
    return Convolution(_FrequencyFourier(layer))
