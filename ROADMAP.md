# Nautical Gourmet Atlas - Roadmap

## V1 (Current) ✅

### Core Features
- [x] User Authentication (Register, Login, JWT)
- [x] Categories & Filters
- [x] Partner Discovery with Map (BBOX queries)
- [x] Partner Details with PIN-based Discounts
- [x] Favorites System
- [x] Visit History & Discount Tracking
- [x] Treasures (Wines, Dishes, Products, Crafts)
- [x] Multi-language Support (HR/EN/DE)

### Technical
- [x] FastAPI Backend with PostGIS
- [x] Expo React Native Mobile App
- [x] Production Docker Setup
- [x] Backend Tests (pytest)
- [x] Mobile Tests (jest)

---

## V2 - Enhanced UX

### Map Integration
- [ ] **Real Mapbox/Google Maps** integration
  - Replace placeholder with actual map SDK
  - Cluster markers for dense areas
  - Animated region changes
- [ ] **GPS Location**
  - "Near me" button with actual GPS
  - Distance-based sorting
  - Walking/Driving directions

### Partner Enhancements
- [ ] **Opening Hours Logic**
  - "Open now" filter (server-side)
  - Show if currently open/closed
  - Next opening time
- [ ] **Reviews & Ratings**
  - User reviews for partners
  - Star ratings
  - Photo uploads by users
- [ ] **QR Code Scanning**
  - Scan QR at partner location
  - Auto-validate discount usage
  - Digital receipt

### Offline Support
- [ ] **Offline Mode**
  - Cache favorites locally
  - Download regions for offline use
  - Sync when online

---

## V3 - Social & Gamification

### Social Features
- [ ] **Share Partners**
  - Share to WhatsApp, Instagram
  - Deep links to app
- [ ] **Trip Planning**
  - Create itineraries
  - Share trips with friends
  - Collaborative trip editing

### Gamification
- [ ] **Achievements & Badges**
  - "Visited 10 partners"
  - "Wine Explorer"
  - "Premium Member"
- [ ] **Points System**
  - Earn points per visit
  - Redeem for exclusive discounts
  - Leaderboard

### Notifications
- [ ] **Push Notifications**
  - New partner nearby
  - Limited time discounts
  - Trip reminders

---

## V4 - Business Features

### Partner Dashboard
- [ ] **Web Admin Panel**
  - Partner self-service
  - Update opening hours
  - View analytics
- [ ] **Analytics**
  - Visit statistics
  - Discount redemption rates
  - Popular times

### Monetization
- [ ] **Premium Subscriptions**
  - Ad-free experience
  - Exclusive discounts
  - Early access to new partners
- [ ] **Partner Fees**
  - Listing fees
  - Featured placement
  - Performance-based pricing

### API Expansion
- [ ] **Public API**
  - Partner integration
  - Third-party apps
  - Tourism board integration

---

## V5 - AI & Personalization

### AI Features
- [ ] **Personalized Recommendations**
  - Based on visit history
  - Preference learning
  - "You might like" suggestions
- [ ] **Smart Search**
  - Natural language queries
  - "Find a romantic dinner spot with wine"
- [ ] **Chatbot Assistant**
  - Trip planning help
  - Restaurant recommendations
  - Real-time Q&A

### AR Features
- [ ] **AR Navigation**
  - Point phone at street, see partners
  - AR discount indicators
- [ ] **AR Menu Preview**
  - View dishes in AR
  - 3D treasure models

---

## Technical Debt & Improvements

### Ongoing
- [ ] **Performance**
  - Image optimization (WebP, lazy loading)
  - API response caching
  - Database query optimization
- [ ] **Security**
  - Rate limiting
  - API key rotation
  - Security audits
- [ ] **Monitoring**
  - Sentry error tracking
  - Performance monitoring
  - Uptime monitoring
- [ ] **CI/CD**
  - GitHub Actions pipeline
  - Automated testing
  - Automated deployments

---

## Release Timeline

| Version | Focus | Target |
|---------|-------|--------|
| V1.0 | Core MVP | ✅ Done |
| V1.1 | Bug fixes, Polish | After user feedback |
| V2.0 | Enhanced UX, Real Maps | Next major |
| V3.0 | Social & Gamification | TBD |
| V4.0 | Business Features | TBD |
| V5.0 | AI & Personalization | TBD |

---

## Contributing

Priorities are determined by:
1. User feedback
2. Business requirements
3. Technical dependencies

For feature requests, open an issue on GitHub.
