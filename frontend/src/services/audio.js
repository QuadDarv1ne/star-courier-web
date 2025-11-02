/**
 * Audio Service for StarCourier Web
 * Handles sound effects and background music
 */

class AudioService {
  constructor() {
    this.audioContext = null;
    this.backgroundMusic = null;
    this.soundEffects = new Map();
    this.isMuted = false;
    this.musicVolume = 0.5;
    this.sfxVolume = 0.7;
    
    // Initialize audio context on first user interaction
    this.initAudioContext();
  }
  
  /**
   * Initialize Web Audio API context
   */
  initAudioContext() {
    // Audio context will be initialized on first user interaction
    // due to browser autoplay policies
  }
  
  /**
   * Create audio context on user interaction
   */
  async createUserContext() {
    if (!this.audioContext) {
      try {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log('Audio context created');
      } catch (e) {
        console.warn('Web Audio API is not supported in this browser', e);
      }
    }
  }
  
  /**
   * Load background music
   * @param {string} url - Music file URL
   */
  loadBackgroundMusic(url) {
    return new Promise((resolve, reject) => {
      if (this.backgroundMusic) {
        this.backgroundMusic.pause();
        this.backgroundMusic = null;
      }
      
      this.backgroundMusic = new Audio(url);
      this.backgroundMusic.loop = true;
      this.backgroundMusic.volume = this.musicVolume;
      
      this.backgroundMusic.addEventListener('loadeddata', () => {
        resolve(this.backgroundMusic);
      });
      
      this.backgroundMusic.addEventListener('error', (e) => {
        reject(new Error(`Failed to load background music: ${e.message}`));
      });
    });
  }
  
  /**
   * Play background music
   */
  async playBackgroundMusic() {
    if (this.isMuted || !this.backgroundMusic) return;
    
    try {
      await this.createUserContext();
      await this.backgroundMusic.play();
      console.log('Background music playing');
    } catch (e) {
      console.warn('Failed to play background music:', e);
    }
  }
  
  /**
   * Pause background music
   */
  pauseBackgroundMusic() {
    if (this.backgroundMusic) {
      this.backgroundMusic.pause();
      console.log('Background music paused');
    }
  }
  
  /**
   * Stop background music
   */
  stopBackgroundMusic() {
    if (this.backgroundMusic) {
      this.backgroundMusic.pause();
      this.backgroundMusic.currentTime = 0;
      console.log('Background music stopped');
    }
  }
  
  /**
   * Set music volume
   * @param {number} volume - Volume level (0.0 to 1.0)
   */
  setMusicVolume(volume) {
    this.musicVolume = Math.max(0, Math.min(1, volume));
    if (this.backgroundMusic) {
      this.backgroundMusic.volume = this.musicVolume;
    }
  }
  
  /**
   * Load sound effect
   * @param {string} name - Sound effect name
   * @param {string} url - Sound file URL
   */
  loadSoundEffect(name, url) {
    return new Promise((resolve, reject) => {
      const audio = new Audio(url);
      audio.volume = this.sfxVolume;
      
      audio.addEventListener('loadeddata', () => {
        this.soundEffects.set(name, audio);
        resolve(audio);
      });
      
      audio.addEventListener('error', (e) => {
        reject(new Error(`Failed to load sound effect '${name}': ${e.message}`));
      });
    });
  }
  
  /**
   * Play sound effect
   * @param {string} name - Sound effect name
   */
  async playSoundEffect(name) {
    if (this.isMuted) return;
    
    const audio = this.soundEffects.get(name);
    if (!audio) {
      console.warn(`Sound effect '${name}' not loaded`);
      return;
    }
    
    try {
      await this.createUserContext();
      // Clone the audio to allow overlapping plays
      const clone = audio.cloneNode();
      clone.volume = this.sfxVolume;
      await clone.play();
    } catch (e) {
      console.warn(`Failed to play sound effect '${name}':`, e);
    }
  }
  
  /**
   * Set sound effects volume
   * @param {number} volume - Volume level (0.0 to 1.0)
   */
  setSfxVolume(volume) {
    this.sfxVolume = Math.max(0, Math.min(1, volume));
    // Update volume for all loaded sound effects
    for (const audio of this.soundEffects.values()) {
      audio.volume = this.sfxVolume;
    }
  }
  
  /**
   * Mute all audio
   */
  mute() {
    this.isMuted = true;
    if (this.backgroundMusic) {
      this.backgroundMusic.pause();
    }
  }
  
  /**
   * Unmute all audio
   */
  unmute() {
    this.isMuted = false;
  }
  
  /**
   * Toggle mute state
   */
  toggleMute() {
    if (this.isMuted) {
      this.unmute();
    } else {
      this.mute();
    }
    return this.isMuted;
  }
}

// Create singleton instance
const audioService = new AudioService();

export default audioService;