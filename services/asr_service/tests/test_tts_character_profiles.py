"""
Unit tests for Character Voice Profiles in TTS Engine
"""

import pytest
from services.asr_service.src.tts_engine import (
    CharacterVoiceProfile,
    TextToSpeech,
    GeraldVoice
)


class TestCharacterVoiceProfile:
    """Test cases for CharacterVoiceProfile"""

    def test_get_available_characters(self):
        """Test getting list of available characters"""
        characters = CharacterVoiceProfile.get_available_characters()

        assert len(characters) == 4
        assert "gerald" in characters
        assert "winnie" in characters
        assert "rapunzel" in characters
        assert "terminator" in characters

    def test_get_profile_gerald(self):
        """Test getting Gerald's profile"""
        profile = CharacterVoiceProfile.get_profile("gerald")

        assert profile is not None
        assert profile["name"] == "Gerald"
        assert "Strict knight" in profile["description"]
        assert "en" in profile
        assert "ru" in profile
        assert profile["en"]["rate"] == 180
        assert profile["en"]["pitch"] == -20
        assert profile["en"]["volume"] == 0.9
        assert profile["en"]["gender"] == "male"

    def test_get_profile_winnie(self):
        """Test getting Winnie's profile"""
        profile = CharacterVoiceProfile.get_profile("winnie")

        assert profile is not None
        assert "Винни Пух" in profile["name"]
        assert "Gentle" in profile["description"]
        assert profile["en"]["rate"] == 140  # Slow, thoughtful
        assert profile["en"]["pitch"] == -10  # Slightly lower, warm
        assert profile["en"]["volume"] == 0.8  # Softer
        assert profile["en"]["gender"] == "male"

    def test_get_profile_rapunzel(self):
        """Test getting Rapunzel's profile"""
        profile = CharacterVoiceProfile.get_profile("rapunzel")

        assert profile is not None
        assert "Rapunzel" in profile["name"]
        assert "cheerful" in profile["description"]
        assert profile["en"]["rate"] == 190  # Energetic
        assert profile["en"]["pitch"] == 15  # Higher, cheerful
        assert profile["en"]["volume"] == 0.85
        assert profile["en"]["gender"] == "female"

    def test_get_profile_terminator(self):
        """Test getting Terminator's profile"""
        profile = CharacterVoiceProfile.get_profile("terminator")

        assert profile is not None
        assert "Терминатор" in profile["name"]
        assert "Robotic" in profile["description"]
        assert profile["en"]["rate"] == 160  # Mechanical
        assert profile["en"]["pitch"] == -30  # Very deep
        assert profile["en"]["volume"] == 1.0  # Loud
        assert profile["en"]["gender"] == "male"

    def test_get_profile_case_insensitive(self):
        """Test that character lookup is case-insensitive"""
        profile_lower = CharacterVoiceProfile.get_profile("gerald")
        profile_upper = CharacterVoiceProfile.get_profile("GERALD")
        profile_mixed = CharacterVoiceProfile.get_profile("Gerald")

        assert profile_lower is not None
        assert profile_upper is not None
        assert profile_mixed is not None
        assert profile_lower == profile_upper == profile_mixed

    def test_get_profile_unknown(self):
        """Test getting unknown character returns None"""
        profile = CharacterVoiceProfile.get_profile("unknown_character")
        assert profile is None

    def test_create_voice_gerald_en(self):
        """Test creating Gerald's English voice"""
        tts = CharacterVoiceProfile.create_voice("gerald", "en")

        assert tts is not None
        assert isinstance(tts, TextToSpeech)
        assert tts.rate == 180
        assert tts.pitch == -20
        assert tts.volume == 0.9
        assert tts.language == "en"

    def test_create_voice_winnie_ru(self):
        """Test creating Winnie's Russian voice"""
        tts = CharacterVoiceProfile.create_voice("winnie", "ru")

        assert tts is not None
        assert isinstance(tts, TextToSpeech)
        assert tts.rate == 135  # Even slower for Russian
        assert tts.pitch == -10
        assert tts.volume == 0.8
        assert tts.language == "ru"

    def test_create_voice_rapunzel_en(self):
        """Test creating Rapunzel's English voice"""
        tts = CharacterVoiceProfile.create_voice("rapunzel", "en")

        assert tts is not None
        assert tts.rate == 190  # Energetic
        assert tts.pitch == 15  # Higher pitch
        assert tts.volume == 0.85

    def test_create_voice_terminator_en(self):
        """Test creating Terminator's English voice"""
        tts = CharacterVoiceProfile.create_voice("terminator", "en")

        assert tts is not None
        assert tts.rate == 160  # Mechanical
        assert tts.pitch == -30  # Very deep
        assert tts.volume == 1.0  # Loud

    def test_create_voice_unknown_character(self):
        """Test creating voice for unknown character returns None"""
        tts = CharacterVoiceProfile.create_voice("unknown", "en")
        assert tts is None

    def test_all_characters_have_both_languages(self):
        """Test that all characters have both English and Russian voices"""
        characters = CharacterVoiceProfile.get_available_characters()

        for char_id in characters:
            profile = CharacterVoiceProfile.get_profile(char_id)
            assert "en" in profile, f"{char_id} missing English voice"
            assert "ru" in profile, f"{char_id} missing Russian voice"

            # Test that both languages can be created
            tts_en = CharacterVoiceProfile.create_voice(char_id, "en")
            tts_ru = CharacterVoiceProfile.create_voice(char_id, "ru")

            assert tts_en is not None, f"{char_id} English voice creation failed"
            assert tts_ru is not None, f"{char_id} Russian voice creation failed"

            # Cleanup
            if tts_en:
                tts_en.shutdown()
            if tts_ru:
                tts_ru.shutdown()

    def test_voice_profile_required_fields(self):
        """Test that all profiles have required fields"""
        required_lang_fields = ["rate", "volume", "pitch", "gender"]
        required_profile_fields = ["name", "description", "en", "ru"]

        characters = CharacterVoiceProfile.get_available_characters()

        for char_id in characters:
            profile = CharacterVoiceProfile.get_profile(char_id)

            # Check profile has required fields
            for field in required_profile_fields:
                assert field in profile, f"{char_id} missing field: {field}"

            # Check language settings have required fields
            for lang in ["en", "ru"]:
                for field in required_lang_fields:
                    assert field in profile[lang], \
                        f"{char_id} {lang} missing field: {field}"

    def test_voice_profiles_have_distinct_settings(self):
        """Test that different characters have distinct voice settings"""
        gerald = CharacterVoiceProfile.get_profile("gerald")
        winnie = CharacterVoiceProfile.get_profile("winnie")
        rapunzel = CharacterVoiceProfile.get_profile("rapunzel")
        terminator = CharacterVoiceProfile.get_profile("terminator")

        # Check that rates are different
        rates = [
            gerald["en"]["rate"],
            winnie["en"]["rate"],
            rapunzel["en"]["rate"],
            terminator["en"]["rate"]
        ]
        assert len(set(rates)) == 4, "All characters should have different rates"

        # Check that pitches are different
        pitches = [
            gerald["en"]["pitch"],
            winnie["en"]["pitch"],
            rapunzel["en"]["pitch"],
            terminator["en"]["pitch"]
        ]
        assert len(set(pitches)) == 4, "All characters should have different pitches"

        # Check gender distribution
        assert gerald["en"]["gender"] == "male"
        assert winnie["en"]["gender"] == "male"
        assert rapunzel["en"]["gender"] == "female"
        assert terminator["en"]["gender"] == "male"

    def test_gerald_voice_backward_compatibility(self):
        """Test that GeraldVoice class still works (backward compatibility)"""
        gerald_en = GeraldVoice.create_english()
        gerald_ru = GeraldVoice.create_russian()

        assert gerald_en is not None
        assert gerald_ru is not None
        assert isinstance(gerald_en, TextToSpeech)
        assert isinstance(gerald_ru, TextToSpeech)

        # Check settings match profile
        profile = CharacterVoiceProfile.get_profile("gerald")
        assert gerald_en.rate == profile["en"]["rate"]
        assert gerald_en.pitch == profile["en"]["pitch"]
        assert gerald_en.volume == profile["en"]["volume"]

        # Cleanup
        gerald_en.shutdown()
        gerald_ru.shutdown()

    def test_character_personality_alignment(self):
        """Test that voice settings align with character personalities"""
        # Gerald - strict, authoritative
        gerald = CharacterVoiceProfile.get_profile("gerald")
        assert gerald["en"]["pitch"] < 0, "Gerald should have lower pitch (authoritative)"
        assert 170 <= gerald["en"]["rate"] <= 190, "Gerald should have steady pace"

        # Winnie - gentle, slow
        winnie = CharacterVoiceProfile.get_profile("winnie")
        assert winnie["en"]["rate"] < 150, "Winnie should be slow (thoughtful)"
        assert winnie["en"]["volume"] < 0.9, "Winnie should be softer (gentle)"

        # Rapunzel - cheerful, energetic
        rapunzel = CharacterVoiceProfile.get_profile("rapunzel")
        assert rapunzel["en"]["pitch"] > 0, "Rapunzel should have higher pitch (cheerful)"
        assert rapunzel["en"]["rate"] > 180, "Rapunzel should be energetic (fast)"

        # Terminator - robotic, stern
        terminator = CharacterVoiceProfile.get_profile("terminator")
        assert terminator["en"]["pitch"] <= -30, "Terminator should have very deep voice"
        assert terminator["en"]["volume"] == 1.0, "Terminator should be loud (commanding)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
