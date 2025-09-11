// Community page JavaScript functionality
document.addEventListener("DOMContentLoaded", () => {
  // Initialize community features
  initializePostFilters()
  initializePostActions()
  initializeModals()
  initializeCommunityFeatures()
})

// Post filtering functionality
function initializePostFilters() {
  const filterButtons = document.querySelectorAll(".filter-buttons .btn")
  const posts = document.querySelectorAll(".post-card")

  filterButtons.forEach((button) => {
    button.addEventListener("click", function () {
      // Update active filter button
      filterButtons.forEach((btn) => btn.classList.remove("active"))
      this.classList.add("active")

      const filter = this.dataset.filter

      // Filter posts
      posts.forEach((post) => {
        if (filter === "all" || post.dataset.category === filter) {
          post.style.display = "block"
          post.style.animation = "fadeIn 0.3s ease"
        } else {
          post.style.display = "none"
        }
      })
    })
  })

  // Sort functionality
  const sortSelect = document.querySelector(".sort-options select")
  if (sortSelect) {
    sortSelect.addEventListener("change", function () {
      sortPosts(this.value)
    })
  }
}

// Post interaction functionality
function initializePostActions() {
  document.addEventListener("click", (e) => {
    // Like button functionality
    if (e.target.closest(".like-btn")) {
      const likeBtn = e.target.closest(".like-btn")
      const countSpan = likeBtn.querySelector("span")
      const count = Number.parseInt(countSpan.textContent)

      if (likeBtn.classList.contains("active")) {
        likeBtn.classList.remove("active")
        countSpan.textContent = count - 1
      } else {
        likeBtn.classList.add("active")
        countSpan.textContent = count + 1
      }
    }

    // Comment button functionality
    if (e.target.closest(".comment-btn")) {
      const postCard = e.target.closest(".post-card")
      const commentsSection = postCard.querySelector(".post-comments")

      // Toggle comments visibility or focus comment input
      if (commentsSection) {
        commentsSection.scrollIntoView({ behavior: "smooth" })
      }
    }

    // Support button functionality
    if (e.target.closest(".support-btn")) {
      const supportBtn = e.target.closest(".support-btn")
      supportBtn.classList.toggle("active")

      if (supportBtn.classList.contains("active")) {
        showSupportMessage()
      }
    }

    // Share button functionality
    if (e.target.closest(".share-btn")) {
      sharePost(e.target.closest(".post-card"))
    }
  })
}

// Modal functionality
function initializeModals() {
  // New post modal
  const newPostModal = document.getElementById("newPostModal")
  if (newPostModal) {
    newPostModal.addEventListener("show.bs.modal", () => {
      // Reset form when modal opens
      document.getElementById("newPostForm").reset()
    })
  }
}

// Community-specific features
function initializeCommunityFeatures() {
  // Load more posts functionality
  const loadMoreBtn = document.getElementById("loadMorePosts")
  if (loadMoreBtn) {
    loadMoreBtn.addEventListener("click", loadMorePosts)
  }

  // Quick action buttons
  initializeQuickActions()

  // Group and event interactions
  initializeGroupActions()
  initializeEventActions()
}

// Quick actions in sidebar
function initializeQuickActions() {
  document.addEventListener("click", (e) => {
    if (e.target.closest('[onclick="joinSupportGroup()"]')) {
      joinSupportGroup()
    }
    if (e.target.closest('[onclick="findMentor()"]')) {
      findMentor()
    }
    if (e.target.closest('[onclick="scheduleCheckIn()"]')) {
      scheduleCheckIn()
    }
  })
}

// Group-related functionality
function initializeGroupActions() {
  const joinGroupBtns = document.querySelectorAll(".group-card .btn, .group-item .btn")

  joinGroupBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const groupName = this.closest(".group-card, .group-item").querySelector(".group-name, .group-title").textContent
      joinGroup(groupName, this)
    })
  })
}

// Event-related functionality
function initializeEventActions() {
  const joinEventBtns = document.querySelectorAll(".event-card .btn-primary")
  const remindBtns = document.querySelectorAll(".event-card .btn-outline-secondary")

  joinEventBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const eventTitle = this.closest(".event-card").querySelector(".event-title").textContent
      joinEvent(eventTitle, this)
    })
  })

  remindBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      const eventTitle = this.closest(".event-card").querySelector(".event-title").textContent
      setEventReminder(eventTitle, this)
    })
  })
}

// Post submission functionality
function submitPost() {
  const form = document.getElementById("newPostForm")
  const formData = new FormData(form)

  const postData = {
    category: document.getElementById("postCategory").value,
    title: document.getElementById("postTitle").value,
    content: document.getElementById("postContent").value,
    tags: document
      .getElementById("postTags")
      .value.split(",")
      .map((tag) => tag.trim())
      .filter((tag) => tag),
    anonymous: document.getElementById("anonymousPost").checked,
    timestamp: new Date().toISOString(),
  }

  // Validate form
  if (!postData.category || !postData.title || !postData.content) {
    alert("Please fill in all required fields.")
    return
  }

  // Here you would typically send to your Flask backend
  console.log("Submitting post:", postData)

  // Simulate post creation
  createNewPostElement(postData)

  // Close modal
  const modal = window.bootstrap.Modal.getInstance(document.getElementById("newPostModal"))
  modal.hide()

  // Show success message
  showSuccessMessage("Your post has been shared with the community!")
}

// Create new post element and add to feed
function createNewPostElement(postData) {
  const postsContainer = document.querySelector(".posts-list")
  const newPost = document.createElement("div")
  newPost.className = `post-card ${postData.category}-post`
  newPost.dataset.category = postData.category

  const categoryInfo = {
    victory: { icon: "fas fa-trophy", label: "Victory", class: "victory" },
    support: { icon: "fas fa-hands-helping", label: "Need Support", class: "support" },
    tips: { icon: "fas fa-lightbulb", label: "Tips & Advice", class: "tips" },
    general: { icon: "fas fa-comments", label: "Discussion", class: "general" },
  }

  const category = categoryInfo[postData.category] || categoryInfo.general
  const authorName = postData.anonymous ? "Anonymous" : "You"

  newPost.innerHTML = `
        <div class="post-header">
            <div class="post-author">
                <img src="/placeholder.svg?height=40&width=40" class="author-avatar" alt="${authorName}">
                <div class="author-info">
                    <h6 class="author-name">${authorName}</h6>
                    <small class="post-time">Just now</small>
                </div>
            </div>
            <div class="post-category ${category.class}">
                <i class="${category.icon}"></i>
                <span>${category.label}</span>
            </div>
        </div>
        <div class="post-content">
            <h5 class="post-title">${postData.title}</h5>
            <p class="post-text">${postData.content}</p>
            ${
              postData.tags.length > 0
                ? `
                <div class="post-tags">
                    ${postData.tags.map((tag) => `<span class="tag">${tag}</span>`).join("")}
                </div>
            `
                : ""
            }
        </div>
        <div class="post-actions">
            <button class="action-btn like-btn">
                <i class="fas fa-heart"></i>
                <span>0</span>
            </button>
            <button class="action-btn comment-btn">
                <i class="fas fa-comment"></i>
                <span>0</span>
            </button>
            <button class="action-btn support-btn">
                <i class="fas fa-hands-helping"></i>
                <span>Support</span>
            </button>
            <button class="action-btn share-btn">
                <i class="fas fa-share"></i>
                <span>Share</span>
            </button>
        </div>
        <div class="post-comments"></div>
    `

  // Add to top of posts list
  postsContainer.insertBefore(newPost, postsContainer.firstChild)

  // Animate in
  newPost.style.opacity = "0"
  newPost.style.transform = "translateY(-20px)"
  setTimeout(() => {
    newPost.style.transition = "all 0.3s ease"
    newPost.style.opacity = "1"
    newPost.style.transform = "translateY(0)"
  }, 100)
}

// Load more posts functionality
function loadMorePosts() {
  const loadMoreBtn = document.getElementById("loadMorePosts")
  loadMoreBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...'
  loadMoreBtn.disabled = true

  // Simulate loading delay
  setTimeout(() => {
    // Here you would typically fetch more posts from your backend
    console.log("Loading more posts...")

    loadMoreBtn.innerHTML = '<i class="fas fa-plus me-2"></i>Load More Posts'
    loadMoreBtn.disabled = false

    // For demo, show message that no more posts are available
    loadMoreBtn.innerHTML = "No more posts to load"
    loadMoreBtn.disabled = true
  }, 1500)
}

// Sort posts functionality
function sortPosts(sortBy) {
  const postsContainer = document.querySelector(".posts-list")
  const posts = Array.from(postsContainer.querySelectorAll(".post-card"))

  posts.sort((a, b) => {
    switch (sortBy) {
      case "popular":
        // Sort by likes (highest first)
        const likesA = Number.parseInt(a.querySelector(".like-btn span").textContent)
        const likesB = Number.parseInt(b.querySelector(".like-btn span").textContent)
        return likesB - likesA

      case "helpful":
        // Sort by comments (highest first)
        const commentsA = Number.parseInt(a.querySelector(".comment-btn span").textContent)
        const commentsB = Number.parseInt(b.querySelector(".comment-btn span").textContent)
        return commentsB - commentsA

      case "recent":
      default:
        // Sort by time (most recent first) - for demo, maintain current order
        return 0
    }
  })

  // Re-append sorted posts
  posts.forEach((post) => postsContainer.appendChild(post))
}

// Community action functions
function joinSupportGroup() {
  showSuccessMessage("Support group recommendations have been sent to your inbox!")
}

function findMentor() {
  showSuccessMessage("Mentor matching process started. You'll be contacted within 24 hours.")
}

function scheduleCheckIn() {
  showSuccessMessage("Check-in reminder has been scheduled. We'll reach out tomorrow.")
}

function joinGroup(groupName, button) {
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'
  button.disabled = true

  setTimeout(() => {
    button.innerHTML = "Joined"
    button.classList.remove("btn-outline-primary")
    button.classList.add("btn-success")
    showSuccessMessage(`You've joined ${groupName}!`)
  }, 1000)
}

function joinEvent(eventTitle, button) {
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'
  button.disabled = true

  setTimeout(() => {
    button.innerHTML = "Joined"
    button.classList.add("btn-success")
    showSuccessMessage(`You've joined "${eventTitle}"! Calendar invite sent.`)
  }, 1000)
}

function setEventReminder(eventTitle, button) {
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>'
  button.disabled = true

  setTimeout(() => {
    button.innerHTML = "Reminder Set"
    button.classList.remove("btn-outline-secondary")
    button.classList.add("btn-info")
    showSuccessMessage(`Reminder set for "${eventTitle}"`)
  }, 1000)
}

// Utility functions
function showSupportMessage() {
  const message = document.createElement("div")
  message.className = "alert alert-success alert-dismissible fade show position-fixed"
  message.style.cssText = "top: 100px; right: 20px; z-index: 1060; max-width: 300px;"
  message.innerHTML = `
        <i class="fas fa-heart me-2"></i>
        Your support means everything to this person.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  document.body.appendChild(message)

  setTimeout(() => {
    if (message.parentNode) {
      message.remove()
    }
  }, 3000)
}

function sharePost(postCard) {
  const postTitle = postCard.querySelector(".post-title").textContent

  if (navigator.share) {
    navigator.share({
      title: postTitle,
      text: "Check out this post from MindSpace Community",
      url: window.location.href,
    })
  } else {
    // Fallback for browsers that don't support Web Share API
    navigator.clipboard.writeText(window.location.href).then(() => {
      showSuccessMessage("Post link copied to clipboard!")
    })
  }
}

function showSuccessMessage(message) {
  const alert = document.createElement("div")
  alert.className = "alert alert-success alert-dismissible fade show position-fixed"
  alert.style.cssText = "top: 100px; right: 20px; z-index: 1060; max-width: 350px;"
  alert.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `

  document.body.appendChild(alert)

  setTimeout(() => {
    if (alert.parentNode) {
      alert.remove()
    }
  }, 4000)
}

// Add CSS animation keyframes
const style = document.createElement("style")
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`
document.head.appendChild(style)

// Declare bootstrap variable
window.bootstrap = window.bootstrap || {}
