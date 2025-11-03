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
    this.isAudioSupported = this.checkAudioSupport();
    
    // Initialize audio context on first user interaction
    this.initAudioContext();
  }
  
  /**
   * Check if audio is supported in the browser
   */
  checkAudioSupport() {
    return !!(window.AudioContext || window.webkitAudioContext);
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
    if (!this.audioContext && this.isAudioSupported) {
      try {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        console.log('Audio context created');
        return true;
      } catch (e) {
        console.warn('Web Audio API is not supported in this browser', e);
        return false;
      }
    }
    return !!this.audioContext;
  }
  
  /**
   * Load background music
   * @param {string} url - Music file URL
   */
  loadBackgroundMusic(url) {
    return new Promise((resolve, reject) => {
      // If we already have background music, clean it up
      if (this.backgroundMusic) {
        this.backgroundMusic.pause();
        this.backgroundMusic = null;
      }
      
      // Create new audio element
      this.backgroundMusic = new Audio(url);
      this.backgroundMusic.loop = true;
      this.backgroundMusic.volume = this.musicVolume;
      
      // Handle load events
      this.backgroundMusic.addEventListener('loadeddata', () => {
        console.log('Background music loaded:', url);
        resolve(this.backgroundMusic);
      });
      
      this.backgroundMusic.addEventListener('error', (e) => {
        console.warn(`Failed to load background music: ${url}`, e);
        // Don't reject, just resolve with null
        resolve(null);
      });
      
      // Try to load the audio
      this.backgroundMusic.load();
    });
  }
  
  /**
   * Play background music
   */
  async playBackgroundMusic() {
    if (this.isMuted || !this.backgroundMusic) return;
    
    try {
      await this.createUserContext();
      // Check if audio is actually loaded
      if (this.backgroundMusic.readyState >= 2) {
        await this.backgroundMusic.play();
        console.log('Background music playing');
      } else {
        console.warn('Background music not ready to play');
      }
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
        console.log('Sound effect loaded:', name, url);
        this.soundEffects.set(name, audio);
        resolve(audio);
      });
      
      audio.addEventListener('error', (e) => {
        console.warn(`Failed to load sound effect '${name}': ${url}`, e);
        // Don't reject, just resolve with null
        resolve(null);
      });
      
      // Try to load the audio
      audio.load();
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
  
  /**
   * Preload all game audio
   */
  async preloadGameAudio() {
    console.log('Preloading game audio...');
    
    try {
      // Load sound effects
      await this.loadSoundEffect('buttonClick', '/audio/sfx/button-click.mp3');
      await this.loadSoundEffect('sceneChange', '/audio/sfx/scene-change.mp3');
      await this.loadSoundEffect('gameOver', '/audio/sfx/game-over.mp3');
      await this.loadSoundEffect('choiceMade', '/audio/sfx/choice-made.mp3');
      await this.loadSoundEffect('achievementUnlocked', '/audio/sfx/achievement.mp3');
      
      // Load background music
      await this.loadBackgroundMusic('/audio/music/background.mp3');
      
      console.log('Audio preloading complete');
      return true;
    } catch (error) {
      console.warn('Failed to preload audio:', error);
      return false;
    }
  }
  
  /**
   * Check if all audio is loaded
   */
  isAudioLoaded() {
    return this.backgroundMusic !== null && this.soundEffects.size > 0;
  }
}

// Create singleton instance
const audioService = new AudioService();

export default audioService;