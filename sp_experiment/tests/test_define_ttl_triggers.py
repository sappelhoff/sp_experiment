"""Test the TTL trigger script for basic integrity."""

from sp_experiment.define_ttl_triggers import provide_trigger_dict


def test_provide_trigger_dict():
    """Test that values in dict are unique."""
    trigger_dict = provide_trigger_dict()

    # Should be a dict of byte values
    assert isinstance(trigger_dict, dict)
    for val in trigger_dict.values():
        assert isinstance(val, bytes)

    # Trigger values should be unique
    trigger_values = list(trigger_dict.values())
    assert len(trigger_values) == len(set(trigger_values))
