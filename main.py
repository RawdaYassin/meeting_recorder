
import recorder
import upload_to_s3

if __name__ == "__main__":
    duration = int(input("Enter recording duration in seconds: "))
    
    from threading import Thread
    
    screen_thread = Thread(target=recorder.record_screen, args=(duration,))
    audio_thread = Thread(target=recorder.record_audio, args=(duration,))
    
    screen_thread.start()
    audio_thread.start()
    
    screen_thread.join()
    audio_thread.join()
    
    recorder.merge_audio_video()
    #upload_to_s3.upload_to_s3()