import speech_recognition as sr
from threading import Thread
import time

class SpeechHandler:
    def __init__(self):
        """Initialize speech recognizer"""
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.last_text = ""
        
        # Adjust for ambient noise
        self.adjust_for_ambient_noise()
    
    def adjust_for_ambient_noise(self):
        """Calibrate microphone for ambient noise"""
        try:
            with sr.Microphone() as source:
                print("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Microphone calibrated successfully")
                return True
        except Exception as e:
            print(f"Error calibrating microphone: {e}")
            return False
    
    def check_microphone(self):
        """Check if microphone is available"""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            if mic_list:
                print(f"Found {len(mic_list)} microphone(s)")
                return True
            else:
                print("No microphones found")
                return False
        except Exception as e:
            print(f"Error checking microphone: {e}")
            return False
    
    def listen_once(self, timeout=5, phrase_time_limit=15):
        """Listen for speech once and return recognized text"""
        try:
            with sr.Microphone() as source:
                print("Listening...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                print("Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                self.last_text = text
                
                print(f"Recognized: {text}")
                return True, text
                
        except sr.WaitTimeoutError:
            return False, "Listening timeout - no speech detected"
        except sr.UnknownValueError:
            return False, "Could not understand audio"
        except sr.RequestError as e:
            return False, f"Could not request results; {e}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def listen_continuous(self, callback, stop_event):
        """
        Continuously listen for speech and call callback with recognized text
        
        Args:
            callback: Function to call with recognized text
            stop_event: Threading event to stop listening
        """
        self.is_listening = True
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while not stop_event.is_set() and self.is_listening:
                try:
                    print("Listening continuously...")
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=10)
                    
                    # Process in background
                    def process_audio():
                        try:
                            text = self.recognizer.recognize_google(audio)
                            self.last_text = text
                            callback(True, text)
                        except sr.UnknownValueError:
                            callback(False, "Could not understand audio")
                        except sr.RequestError as e:
                            callback(False, f"API error: {e}")
                        except Exception as e:
                            callback(False, f"Error: {e}")
                    
                    # Process in separate thread to not block listening
                    Thread(target=process_audio, daemon=True).start()
                    
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    print(f"Listening error: {e}")
                    time.sleep(0.5)
        
        self.is_listening = False
    
    def stop_listening(self):
        """Stop continuous listening"""
        self.is_listening = False
    
    def get_last_text(self):
        """Get last recognized text"""
        return self.last_text
    
    def test_microphone(self):
        """Test microphone with simple recording"""
        try:
            print("=== Microphone Test ===")
            print("Available microphones:")
            for i, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"  {i}: {name}")
            
            print("\nTesting microphone... Speak now!")
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Listening for 3 seconds...")
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=3)
                
                print("Processing...")
                text = self.recognizer.recognize_google(audio)
                print(f"You said: {text}")
                return True, text
                
        except Exception as e:
            print(f"Test failed: {e}")
            return False, str(e)


class SpeechRecognitionWidget:
    """Widget for speech recognition UI"""
    
    def __init__(self, parent, speech_handler):
        self.parent = parent
        self.speech_handler = speech_handler
        self.callback = None
        self.is_recording = False
    
    def set_callback(self, callback):
        """Set callback function for recognized speech"""
        self.callback = callback
    
    def start_recording(self):
        """Start recording speech"""
        if self.is_recording:
            return
        
        self.is_recording = True
        
        # Start listening in separate thread
        def listen_thread():
            success, text = self.speech_handler.listen_once()
            self.is_recording = False
            
            if self.callback:
                self.callback(success, text)
        
        Thread(target=listen_thread, daemon=True).start()
    
    def stop_recording(self):
        """Stop recording"""
        self.speech_handler.stop_listening()
        self.is_recording = False