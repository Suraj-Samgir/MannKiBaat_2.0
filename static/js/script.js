// Dashboard JavaScript functionality
document.addEventListener("DOMContentLoaded", () => {
  // Declare all variables at the top
  let chatWindow, chatOverlay, chatMessages, chatInput, sendBtn
  const crisisDetectionActive = false
  let crisisKeywordCount = 0
  let lastCrisisCheck = null
  let isTyping = false
  const messageHistory = []

  // Initialize chat elements
  chatWindow = document.getElementById("chatWindow")
  chatOverlay = document.getElementById("chatOverlay")
  chatMessages = document.getElementById("chatMessages")
  chatInput = document.getElementById("chatInput")
  sendBtn = document.getElementById("sendBtn")

  // Mood tracking functionality
  const moodButtons = document.querySelectorAll(".mood-btn")
  moodButtons.forEach((btn) => {
    btn.addEventListener("click", function () {
      // Remove selected class from all buttons
      moodButtons.forEach((b) => b.classList.remove("selected"))
      // Add selected class to clicked button
      this.classList.add("selected")

      const mood = this.dataset.mood
      console.log("Mood selected:", mood)

      const moodScores = {
        excellent: 5,
        good: 4,
        okay: 3,
        low: 2,
        struggling: 1,
      }

      const moodScore = moodScores[mood] || 3

      // Send mood data to Flask backend
      fetch("/api/mood", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          mood_score: moodScore,
          notes: `Mood: ${mood}`,
          timestamp: new Date().toISOString(),
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          console.log("Mood logged successfully:", data)
          showMoodFeedback(mood)
        })
        .catch((error) => {
          console.error("Error logging mood:", error)
          alert("Failed to log mood. Please try again.")
        })

      // Show crisis alert for struggling mood
      if (mood === "struggling" || mood === "low") {
        showCrisisAlert()
      }
    })
  })

  // Crisis alert functionality
  function showCrisisAlert() {
    const crisisAlert = document.getElementById("crisis-alert")
    crisisAlert.classList.remove("d-none")

    // Show crisis indicator
    showCrisisIndicator()

    // Log crisis event for backend
    logCrisisEvent("mood_based_trigger")

    // Auto-hide after 30 seconds if not interacted with
    setTimeout(() => {
      if (!crisisAlert.classList.contains("d-none")) {
        crisisAlert.classList.add("d-none")
      }
    }, 30000)
  }

  function dismissCrisisAlert() {
    document.getElementById("crisis-alert").classList.add("d-none")
    hideCrisisIndicator()

    // Log dismissal
    logCrisisEvent("alert_dismissed")
  }

  function showCrisisIndicator() {
    let indicator = document.getElementById("crisisIndicator")

    if (!indicator) {
      indicator = document.createElement("div")
      indicator.id = "crisisIndicator"
      indicator.className = "crisis-indicator"
      indicator.innerHTML = `
        <div class="indicator-content">
          <div class="indicator-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="indicator-text">
            Crisis Support<br>
            <small>Click for help</small>
          </div>
        </div>
      `
      indicator.onclick = () => openCrisisModal()
      document.body.appendChild(indicator)
    }

    setTimeout(() => {
      indicator.classList.add("show")
    }, 100)
  }

  function hideCrisisIndicator() {
    const indicator = document.getElementById("crisisIndicator")
    if (indicator) {
      indicator.classList.remove("show")
    }
  }

  function openCrisisModal() {
    const modal = new window.bootstrap.Modal(document.getElementById("crisisModal"))
    modal.show()

    // Hide crisis indicator when modal opens
    hideCrisisIndicator()

    // Log modal opening
    logCrisisEvent("modal_opened")
  }

  // Crisis alert dismiss functionality
  document.addEventListener("click", (e) => {
    if (e.target.closest(".crisis-actions .btn")) {
      const action = e.target.textContent.trim()
      console.log("Crisis action:", action)

      if (action === "I'm okay") {
        dismissCrisisAlert()
      }
      // Handle other crisis actions here
    }
  })

  // Activity button functionality
  document.addEventListener("click", (e) => {
    if (e.target.closest(".activity-item .btn")) {
      const activityName = e.target.closest(".activity-item").querySelector("h6").textContent
      console.log("Starting activity:", activityName)

      // Here you would typically navigate to the activity or open a modal
      alert(`Starting: ${activityName}`)
    }
  })

  // Affirmation actions
  document.addEventListener("click", (e) => {
    if (e.target.closest(".affirmation-actions .btn")) {
      const action = e.target.textContent.trim()
      console.log("Affirmation action:", action)

      if (action === "New One") {
        // Generate new affirmation
        generateNewAffirmation()
      } else if (action === "Listen") {
        // Play audio affirmation
        playAudioAffirmation()
      } else if (action === "Watch") {
        // Play video affirmation
        playVideoAffirmation()
      }
    }
  })

  // Achievement click functionality
  document.addEventListener("click", (e) => {
    if (e.target.closest(".achievement-item")) {
      const achievementName = e.target.closest(".achievement-item").querySelector(".achievement-name").textContent
      console.log("Achievement clicked:", achievementName)

      // Show achievement details modal
      showAchievementDetails(achievementName)
    }
  })

  // Navigation functionality
  document.addEventListener("click", (e) => {
    if (e.target.closest(".nav-link")) {
      const navLinks = document.querySelectorAll(".nav-link")
      navLinks.forEach((link) => link.classList.remove("active"))
      e.target.closest(".nav-link").classList.add("active")
    }
  })

  // Floating chat button functionality
  document.getElementById("chatBtn").addEventListener("click", () => {
    toggleChatWindow()
  })

  // Chat window controls
  document.getElementById("closeChat").addEventListener("click", closeChatWindow)
  document.getElementById("minimizeChat").addEventListener("click", minimizeChatWindow)

  // Chat overlay click to close
  chatOverlay.addEventListener("click", closeChatWindow)

  // Send message functionality
  sendBtn.addEventListener("click", sendMessage)
  chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  })

  // Quick response buttons
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("quick-response-btn")) {
      const response = e.target.dataset.response
      sendUserMessage(response)
      e.target.style.display = "none" // Hide used quick response
    }
  })

  // Chat input character counter and validation
  chatInput.addEventListener("input", function () {
    const length = this.value.length
    const maxLength = 500

    if (length > maxLength - 50) {
      // Show warning when approaching limit
      console.log(`Characters remaining: ${maxLength - length}`)
    }

    // Enable/disable send button
    sendBtn.disabled = this.value.trim().length === 0
  })

  // Voice message functionality
  document.getElementById("voiceBtn").addEventListener("click", () => {
    toggleVoiceRecording()
  })

  // Mood sharing functionality
  document.getElementById("moodBtn").addEventListener("click", () => {
    showMoodSelector()
  })

  // Emergency resources
  document.getElementById("emergencyBtn").addEventListener("click", () => {
    showEmergencyResources()
  })

  // Chat window management functions
  function toggleChatWindow() {
    if (chatWindow.classList.contains("show")) {
      closeChatWindow()
    } else {
      openChatWindow()
    }
  }

  function openChatWindow() {
    chatWindow.classList.add("show")
    chatWindow.classList.remove("minimized")

    // Show overlay on mobile
    if (window.innerWidth <= 768) {
      chatOverlay.classList.add("show")
      document.body.style.overflow = "hidden"
    }

    // Focus input
    setTimeout(() => {
      chatInput.focus()
    }, 300)

    // Clear notification badge
    const notification = document.querySelector(".chat-notification")
    if (notification) {
      notification.textContent = "0"
      notification.style.display = "none"
    }

    // Scroll to bottom
    scrollToBottom()
  }

  function closeChatWindow() {
    chatWindow.classList.remove("show")
    chatOverlay.classList.remove("show")
    document.body.style.overflow = ""
  }

  function minimizeChatWindow() {
    chatWindow.classList.add("minimized")
  }

  // Message handling functions
  function sendMessage() {
    const message = chatInput.value.trim()
    if (message && !isTyping) {
      sendUserMessage(message)
      chatInput.value = ""
      sendBtn.disabled = true
    }
  }

  function sendUserMessage(message) {
    // Add user message to chat
    addMessage(message, "user")

    // Store in history
    messageHistory.push({ role: "user", content: message, timestamp: new Date() })

    // Show typing indicator
    showTypingIndicator()

    // Simulate AI response (replace with actual API call)
    setTimeout(
      () => {
        generateBotResponse(message)
      },
      1000 + Math.random() * 2000,
    ) // Random delay 1-3 seconds
  }

  function addMessage(content, sender, timestamp = null) {
    const messageDiv = document.createElement("div")
    messageDiv.className = `message ${sender}-message`

    const avatarDiv = document.createElement("div")
    avatarDiv.className = "message-avatar"
    avatarDiv.innerHTML = sender === "bot" ? '<i class="fas fa-robot"></i>' : '<i class="fas fa-user"></i>'

    const contentDiv = document.createElement("div")
    contentDiv.className = "message-content"

    const bubbleDiv = document.createElement("div")
    bubbleDiv.className = "message-bubble"
    bubbleDiv.innerHTML = `<p>${content}</p>`

    const timeDiv = document.createElement("div")
    timeDiv.className = "message-time"
    timeDiv.textContent = timestamp || formatTime(new Date())

    contentDiv.appendChild(bubbleDiv)
    contentDiv.appendChild(timeDiv)

    messageDiv.appendChild(avatarDiv)
    messageDiv.appendChild(contentDiv)

    chatMessages.appendChild(messageDiv)
    scrollToBottom()
  }

  function generateBotResponse(userMessage) {
    hideTypingIndicator()

    // Simple response generation (replace with actual AI API)
    const response = getBotResponse(userMessage)

    // Add bot message
    addMessage(response, "bot")

    // Store in history
    messageHistory.push({ role: "bot", content: response, timestamp: new Date() })

    // Check for crisis keywords and show appropriate response
    if (containsCrisisKeywords(userMessage)) {
      setTimeout(() => {
        addMessage(
          "I'm concerned about what you've shared. Would you like me to connect you with professional support resources?",
          "bot",
        )
        showCrisisOptions()
      }, 1000)
    }
  }

  function getBotResponse(message) {
    const lowerMessage = message.toLowerCase()

    // Empathetic responses based on keywords
    if (lowerMessage.includes("anxious") || lowerMessage.includes("anxiety")) {
      return "I understand that anxiety can feel overwhelming. It's completely normal to feel this way sometimes. Would you like to try a quick breathing exercise together, or would you prefer to talk about what's making you feel anxious?"
    }

    if (lowerMessage.includes("sad") || lowerMessage.includes("depressed") || lowerMessage.includes("down")) {
      return "I hear that you're going through a difficult time, and I want you to know that your feelings are valid. It takes courage to reach out. What's been weighing on your mind lately?"
    }

    if (lowerMessage.includes("good day") || lowerMessage.includes("happy") || lowerMessage.includes("great")) {
      return "That's wonderful to hear! I'm glad you're having a good day. What made today special for you? Celebrating these positive moments is important for your wellbeing."
    }

    if (lowerMessage.includes("stress") || lowerMessage.includes("overwhelmed")) {
      return "Feeling stressed or overwhelmed is something many people experience. You're not alone in this. Would you like to explore some stress management techniques, or would you prefer to talk about what's causing these feelings?"
    }

    if (lowerMessage.includes("help") || lowerMessage.includes("support")) {
      return "I'm here to support you in whatever way I can. Whether you need someone to listen, want to explore coping strategies, or need resources for professional help, I'm here. What kind of support would be most helpful right now?"
    }

    if (lowerMessage.includes("relax") || lowerMessage.includes("calm")) {
      return "Let's work on finding some calm together. I can guide you through a relaxation exercise, suggest some mindfulness techniques, or we can simply talk about peaceful things. What sounds most appealing to you?"
    }

    // Default empathetic response
    const defaultResponses = [
      "Thank you for sharing that with me. I'm here to listen and support you. Can you tell me more about how you're feeling?",
      "I appreciate you opening up. Your feelings and experiences matter. What's been the most challenging part of your day?",
      "It sounds like you have a lot going on. I'm here to help you work through whatever you're facing. What would be most helpful to talk about?",
      "I'm glad you reached out. Sometimes just talking can help us process our thoughts and feelings. What's been the most difficult thing you've faced today?",
    ]

    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)]
  }

  function containsCrisisKeywords(message) {
    const crisisKeywords = [
      // Suicide ideation
      "suicide",
      "kill myself",
      "end it all",
      "not worth living",
      "better off dead",
      "want to die",
      "wish I was dead",
      "end my life",
      "take my own life",

      // Self-harm
      "hurt myself",
      "self harm",
      "cutting",
      "cut myself",
      "harm myself",
      "self injury",
      "burning myself",
      "hitting myself",

      // Hopelessness
      "hopeless",
      "no point",
      "nothing matters",
      "give up",
      "can't go on",
      "no way out",
      "trapped",
      "worthless",
      "burden",
      "everyone hates me",

      // Crisis indicators
      "overdose",
      "pills",
      "rope",
      "bridge",
      "jump",
      "gun",
      "knife",
    ]

    const lowerMessage = message.toLowerCase()
    const foundKeywords = crisisKeywords.filter((keyword) => lowerMessage.includes(keyword))

    if (foundKeywords.length > 0) {
      crisisKeywordCount += foundKeywords.length
      lastCrisisCheck = new Date()

      // Escalate based on keyword severity and frequency
      if (
        foundKeywords.some((kw) => ["suicide", "kill myself", "end my life"].includes(kw)) ||
        crisisKeywordCount >= 3
      ) {
        triggerHighRiskAlert()
      }

      return true
    }

    return false
  }

  function triggerHighRiskAlert() {
    // Immediate crisis response
    showCrisisAlert()
    showCrisisIndicator()

    // Auto-open crisis modal for high-risk situations
    setTimeout(() => {
      openCrisisModal()
    }, 2000)

    // Log high-risk event
    logCrisisEvent("high_risk_detected", { keywordCount: crisisKeywordCount })
  }

  function showCrisisOptions() {
    const crisisDiv = document.createElement("div")
    crisisDiv.className = "crisis-options"
    crisisDiv.innerHTML = `
        <div class="crisis-buttons">
            <button class="btn btn-danger btn-sm crisis-btn" onclick="callCrisisHotline()">
                <i class="fas fa-phone me-1"></i>Crisis Hotline
            </button>
            <button class="btn btn-warning btn-sm crisis-btn" onclick="openCrisisChat()">
                <i class="fas fa-comments me-1"></i>Chat with Counselor
            </button>
            <button class="btn btn-info btn-sm crisis-btn" onclick="openTextCrisis()">
                <i class="fas fa-heart me-1"></i>Text Crisis Line
            </button>
            <button class="btn btn-success btn-sm crisis-btn" onclick="callEmergency()">
                <i class="fas fa-hospital me-1"></i>Emergency Services
            </button>
            <button class="btn btn-primary btn-sm crisis-btn" onclick="openPeerSupport()">
                <i class="fas fa-users me-1"></i>Peer Support
            </button>
            <button class="btn btn-secondary btn-sm crisis-btn" onclick="openSelfCareTools()">
                <i class="fas fa-hand-holding-heart me-1"></i>Self-Care Tools
            </button>
        </div>
    `

    chatMessages.appendChild(crisisDiv)
    scrollToBottom()
  }

  // Utility functions
  function showTypingIndicator() {
    isTyping = true
    document.getElementById("typingIndicator").classList.remove("d-none")
    scrollToBottom()
  }

  function hideTypingIndicator() {
    isTyping = false
    document.getElementById("typingIndicator").classList.add("d-none")
  }

  function scrollToBottom() {
    setTimeout(() => {
      chatMessages.scrollTop = chatMessages.scrollHeight
    }, 100)
  }

  function formatTime(date) {
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  // Feature functions
  function toggleVoiceRecording() {
    const voiceBtn = document.getElementById("voiceBtn")

    if (voiceBtn.classList.contains("active")) {
      // Stop recording
      voiceBtn.classList.remove("active")
      voiceBtn.innerHTML = '<i class="fas fa-microphone"></i>'
      console.log("Voice recording stopped")
      // Here you would stop the actual voice recording
    } else {
      // Start recording
      voiceBtn.classList.add("active")
      voiceBtn.innerHTML = '<i class="fas fa-stop"></i>'
      console.log("Voice recording started")
      // Here you would start the actual voice recording
    }
  }

  function showMoodSelector() {
    const moodMessage = "How are you feeling right now?"
    addMessage(moodMessage, "bot")

    // Add mood selector buttons
    const moodDiv = document.createElement("div")
    moodDiv.className = "mood-selector"
    moodDiv.innerHTML = `
        <div class="mood-options">
            <button class="mood-option" onclick="selectChatMood('😊', 'Great')">😊 Great</button>
            <button class="mood-option" onclick="selectChatMood('🙂', 'Good')">🙂 Good</button>
            <button class="mood-option" onclick="selectChatMood('😐', 'Okay')">😐 Okay</button>
            <button class="mood-option" onclick="selectChatMood('😔', 'Low')">😔 Low</button>
            <button class="mood-option" onclick="selectChatMood('😢', 'Struggling')">😢 Struggling</button>
        </div>
    `

    chatMessages.appendChild(moodDiv)
    scrollToBottom()
  }

  function showEmergencyResources() {
    const emergencyMessage = `
        <strong>Emergency Resources:</strong><br><br>
        🚨 <strong>Crisis Hotline:</strong> 988 (24/7)<br>
        💬 <strong>Crisis Text Line:</strong> Text HOME to 741741<br>
        🏥 <strong>Emergency:</strong> Call 911<br><br>
        <em>You are not alone. Help is available 24/7.</em>
    `

    addMessage(emergencyMessage, "bot")
  }

  function logCrisisEvent(eventType, data = {}) {
    const event = {
      type: eventType,
      timestamp: new Date().toISOString(),
      userId: "current_user_id", // Replace with actual user ID
      sessionId: "current_session_id", // Replace with actual session ID
      ...data,
    }

    console.log("Crisis Event:", event)

    // In production, send to backend for monitoring and follow-up
    // fetch('/api/crisis-events', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   body: JSON.stringify(event)
    // })
  }

  // Periodic crisis check
  setInterval(
    () => {
      if (lastCrisisCheck && crisisKeywordCount > 0) {
        const timeSinceLastCrisis = new Date() - lastCrisisCheck

        // If it's been more than 30 minutes since last crisis indicator, show gentle check-in
        if (timeSinceLastCrisis > 30 * 60 * 1000) {
          showGentleCheckIn()
          crisisKeywordCount = 0 // Reset counter
        }
      }
    },
    5 * 60 * 1000,
  ) // Check every 5 minutes

  function showGentleCheckIn() {
    const checkInMessage =
      "I noticed you might have been going through a difficult time earlier. How are you feeling now? Remember, I'm here if you need support."

    addMessage(checkInMessage, "bot")

    // Add quick check-in options
    const checkInDiv = document.createElement("div")
    checkInDiv.className = "check-in-options"
    checkInDiv.innerHTML = `
      <div class="quick-responses">
        <button class="quick-response-btn" onclick="respondToCheckIn('better')">I'm feeling better</button>
        <button class="quick-response-btn" onclick="respondToCheckIn('same')">About the same</button>
        <button class="quick-response-btn" onclick="respondToCheckIn('worse')">I'm struggling</button>
        <button class="quick-response-btn" onclick="openCrisisModal()">I need help</button>
      </div>
    `

    chatMessages.appendChild(checkInDiv)
    scrollToBottom()
  }

  // Make functions available globally for onclick handlers
  window.showCrisisAlert = showCrisisAlert
  window.showCrisisIndicator = showCrisisIndicator
  window.openCrisisModal = openCrisisModal
  window.dismissCrisisAlert = dismissCrisisAlert
  window.showMoodFeedback = showMoodFeedback

  function showMoodFeedback(mood) {
    const feedbackMessages = {
      excellent: "Great to hear you're feeling excellent! Keep up the positive energy! 🌟",
      good: "Glad you're having a good day! What's contributing to your positive mood? 😊",
      okay: "Thanks for checking in. Is there anything that might help you feel a bit better? 🤗",
      low: "I understand you're feeling low. Remember, it's okay to have difficult days. Would you like some support? 💙",
      struggling: "I'm concerned about you. You're brave for reaching out. Let's find some support together. 🤝",
    }

    const message = feedbackMessages[mood] || "Thanks for sharing your mood with me."

    // Show temporary feedback message
    const feedbackDiv = document.createElement("div")
    feedbackDiv.className = "mood-feedback alert alert-success mt-3"
    feedbackDiv.style.cssText = "position: relative; z-index: 1000; animation: fadeIn 0.3s ease-in;"
    feedbackDiv.innerHTML = `
      <div class="d-flex align-items-center">
        <i class="fas fa-heart me-2 text-danger"></i>
        <span>${message}</span>
        <button type="button" class="btn-close ms-auto" onclick="this.parentElement.parentElement.remove()"></button>
      </div>
    `

    // Find the mood tracking section and add feedback
    const moodSection = document.querySelector(".mood-tracking") || document.querySelector(".card-body")
    if (moodSection) {
      // Remove any existing feedback first
      const existingFeedback = moodSection.querySelector(".mood-feedback")
      if (existingFeedback) {
        existingFeedback.remove()
      }

      moodSection.appendChild(feedbackDiv)

      // Add CSS animation
      const style = document.createElement("style")
      style.textContent = `
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(-10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeOut {
          from { opacity: 1; transform: translateY(0); }
          to { opacity: 0; transform: translateY(-10px); }
        }
      `
      document.head.appendChild(style)

      // Remove feedback after 8 seconds
      setTimeout(() => {
        if (feedbackDiv && feedbackDiv.parentNode) {
          feedbackDiv.style.animation = "fadeOut 0.3s ease-out"
          setTimeout(() => feedbackDiv.remove(), 300)
        }
      }, 8000)
    } else {
      // Fallback: show as browser alert if no container found
      alert(message)
    }

    console.log("[v0] Mood feedback displayed:", mood, message)
  }
})

// Helper functions (outside DOMContentLoaded for global access)
function generateNewAffirmation() {
  const affirmations = [
    "You are stronger than you think and braver than you feel. Every challenge you face is making you more resilient.",
    "Your mental health journey is unique and valid. Every small step forward is worth celebrating.",
    "You have the power to create positive change in your life, one day at a time.",
    "It's okay to not be okay sometimes. What matters is that you're here and you're trying.",
    "You are worthy of love, kindness, and all the good things life has to offer.",
  ]

  const randomAffirmation = affirmations[Math.floor(Math.random() * affirmations.length)]
  document.querySelector(".affirmation-text").textContent = `"${randomAffirmation}"`
}

function playAudioAffirmation() {
  // This would integrate with text-to-speech API
  console.log("Playing audio affirmation")
  alert("Audio affirmation would play here (integrate with TTS API)")
}

function playVideoAffirmation() {
  // This would show video affirmation
  console.log("Playing video affirmation")
  alert("Video affirmation would play here")
}

function showAchievementDetails(achievementName) {
  // This would show a modal with achievement details
  console.log("Showing details for:", achievementName)
  alert(`Achievement: ${achievementName}\n\nDetails about this achievement would be shown here.`)
}

// Simulated real-time updates
function simulateRealTimeUpdates() {
  // Update community stats periodically
  setInterval(() => {
    const activeMembers = document.querySelector(".stat-number")
    if (activeMembers) {
      const currentCount = Number.parseInt(activeMembers.textContent.replace(",", ""))
      const newCount = currentCount + Math.floor(Math.random() * 5)
      activeMembers.textContent = newCount.toLocaleString()
    }
  }, 30000) // Update every 30 seconds

  // Update chat notification badge
  setInterval(() => {
    const chatNotification = document.querySelector(".chat-notification")
    if (chatNotification) {
      const currentCount = Number.parseInt(chatNotification.textContent)
      if (Math.random() > 0.7) {
        // 30% chance of new message
        chatNotification.textContent = currentCount + 1
      }
    }
  }, 15000) // Check every 15 seconds
}

// Initialize real-time updates
simulateRealTimeUpdates()

// Crisis resource functions (global for onclick handlers)
function callCrisisHotline() {
  console.log("Crisis hotline called")

  // For mobile devices, directly call
  if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    window.location.href = "tel:988"
  } else {
    // For desktop, show instructions
    alert("Crisis Hotline: 988\n\nThis number is available 24/7 for crisis support.")
  }
}

function openCrisisChat() {
  console.log("Crisis chat opened")
  alert("Connecting to crisis counselor...\n\nThis would integrate with a real crisis chat service.")
}

function openTextCrisis() {
  console.log("Text crisis opened")

  if (/Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    window.location.href = "sms:741741?body=HOME"
  } else {
    alert("Crisis Text Line: Text HOME to 741741\n\nThis service is available 24/7.")
  }
}

function callEmergency() {
  console.log("Emergency called")

  if (confirm("This will call emergency services (911). Do you want to proceed?")) {
    window.location.href = "tel:911"
  }
}

function openPeerSupport() {
  console.log("Peer support opened")
  alert("Connecting to peer support groups...\n\nThis would integrate with community support features.")
}

function openSelfCareTools() {
  console.log("Self care opened")
  alert("Opening self-care tools...\n\nThis would show immediate coping strategies.")
}

function saveSafetyPlan() {
  const trustedContact = document.getElementById("trustedContact")?.value
  const safePlace = document.getElementById("safePlace")?.value
  const copingStrategies = document.getElementById("copingStrategies")?.value

  if (!trustedContact || !safePlace || !copingStrategies) {
    alert("Please fill in all fields to create your safety plan.")
    return
  }

  const safetyPlan = {
    trustedContact,
    safePlace,
    copingStrategies,
    createdAt: new Date().toISOString(),
  }

  // Save to localStorage (in production, save to backend)
  localStorage.setItem("safetyPlan", JSON.stringify(safetyPlan))

  alert("Your safety plan has been saved. You can access it anytime from your profile.")

  // Clear form
  if (document.getElementById("trustedContact")) document.getElementById("trustedContact").value = ""
  if (document.getElementById("safePlace")) document.getElementById("safePlace").value = ""
  if (document.getElementById("copingStrategies")) document.getElementById("copingStrategies").value = ""
}

function shareWithTrustedPerson() {
  const safetyPlan = localStorage.getItem("safetyPlan")

  if (!safetyPlan) {
    alert("Please create a safety plan first.")
    return
  }

  alert(
    "Safety plan sharing feature would be implemented here.\n\nThis could send an email or text to your trusted contact.",
  )
}

function findLocalResources() {
  alert(
    "Local mental health resource finder would be implemented here.\n\nThis could use geolocation to find nearby services.",
  )
}

function scheduleAppointment() {
  alert("Appointment scheduling would be implemented here.\n\nThis could connect with local mental health providers.")
}

function selectChatMood(emoji, mood) {
  const moodScores = {
    Great: 5,
    Good: 4,
    Okay: 3,
    Low: 2,
    Struggling: 1,
  }

  const moodScore = moodScores[mood] || 3

  // Send mood data to Flask backend
  fetch("/api/mood", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mood_score: moodScore,
      notes: `Chat mood: ${mood} ${emoji}`,
      timestamp: new Date().toISOString(),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Chat mood logged successfully:", data)
    })
    .catch((error) => {
      console.error("Error logging chat mood:", error)
    })

  // Remove mood selector
  const moodSelector = document.querySelector(".mood-selector")
  if (moodSelector) {
    moodSelector.remove()
  }

  // Add user message showing selected mood
  if (window.addMessage) {
    window.addMessage(`I'm feeling ${mood} ${emoji}`, "user")
  }
}

function respondToCheckIn(response) {
  const responses = {
    better: "I'm glad to hear you're feeling better. That takes strength. Is there anything specific that helped?",
    same: "Thank you for letting me know. Sometimes staying steady is an achievement in itself. What would help you feel a bit better right now?",
    worse:
      "I'm concerned about you. You don't have to go through this alone. Would you like to talk about what's making things harder, or would you prefer some immediate support resources?",
  }

  alert(`You selected: ${response}\n\nBot would respond: ${responses[response]}`)

  // Remove check-in options
  const checkInOptions = document.querySelector(".check-in-options")
  if (checkInOptions) {
    checkInOptions.remove()
  }

  if (response === "worse") {
    setTimeout(() => {
      if (window.showCrisisAlert) {
        window.showCrisisAlert()
      }
    }, 1000)
  }
}

// Declare bootstrap variable
window.bootstrap = window.bootstrap || {}
