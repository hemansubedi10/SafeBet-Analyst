"""
SafeBet Analyst - Bet Scraper Module
Handles scraping bet data from 1xBet account
Secure read-only access without financial transaction capabilities
"""

import asyncio
from playwright.async_api import async_playwright
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BetScraper:
    def __init__(self):
        self.browser = None
        self.page = None
        self.username = None
        self.password = None

    async def initialize(self, headless=True):
        """Initialize the Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.page = await self.browser.new_page()

        # Set user agent to appear more human-like
        await self.page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

        # Set viewport to appear like a real user
        await self.page.set_viewport_size({"width": 1920, "height": 1080})

    async def login(self, username=None, password=None):
        """Login to 1xBet account with credentials"""
        # Use provided credentials or environment variables
        self.username = username or os.getenv("XBET_USERNAME")
        self.password = password or os.getenv("XBET_PASSWORD")

        if not self.username or not self.password:
            raise ValueError("Username and password must be provided or set in environment variables")

        # Navigate to login page
        await self.page.goto("https://1xbet.com/en/login")

        # Wait for login form to load
        await self.page.wait_for_selector('input[name="login"]', timeout=10000)

        # Fill in credentials
        await self.page.fill('input[name="login"]', self.username)
        await self.page.fill('input[name="password"]', self.password)

        # Click login button
        await self.page.click('button[type="submit"]')

        # Wait for login to complete
        await self.page.wait_for_timeout(5000)

        # Verify login by checking if we're redirected to office or profile
        current_url = self.page.url
        if "office" in current_url or "profile" in current_url:
            print("Login successful")
            return True
        else:
            raise Exception("Login failed - could not verify login state")

    async def navigate_to_history(self):
        """Navigate to the bet history page - READ ONLY ACCESS"""
        # Go directly to the history page
        await self.page.goto("https://1xbet.com/en/office/history")

        # Wait for page to load
        await self.page.wait_for_selector('.history-table, .bet-slip-history', timeout=15000)

        # Verify we're on the right page and not on payment/deposit sections
        current_url = self.page.url
        if "payment" in current_url.lower() or "deposit" in current_url.lower() or "withdraw" in current_url.lower():
            raise Exception("Security violation: Navigated to payment section unexpectedly")

    async def scrape_bets(self):
        """Scrape bet data from the history page - READ ONLY"""
        # Wait for the bet history to load
        await self.page.wait_for_selector('.bet-item, .history-line', timeout=15000)

        # Extract bet data using JavaScript evaluation
        # This is read-only and does not interact with any betting functions
        bets_data = await self.page.evaluate("""
            () => {
                // Look for different possible selectors for bet items
                const betElements = document.querySelectorAll('.bet-item, .history-line, .bet-slip-item');
                const bets = [];

                for (const element of betElements) {
                    try {
                        // Extract match name
                        const matchNameEl = element.querySelector('.match-name') ||
                                          element.querySelector('.event-name') ||
                                          element.querySelector('[data-event-name]') ||
                                          element.querySelector('.team-name') ||
                                          element.querySelector('.participant');
                        const matchName = matchNameEl ? matchNameEl.textContent.trim() : 'Unknown Match';

                        // Extract bet type
                        const betTypeEl = element.querySelector('.bet-type') ||
                                        element.querySelector('.selection') ||
                                        element.querySelector('.bet-desc') ||
                                        element.querySelector('.outcome');
                        const betType = betTypeEl ? betTypeEl.textContent.trim() : 'Unknown Bet Type';

                        // Extract odds
                        const oddsEl = element.querySelector('.odds') ||
                                     element.querySelector('.coeff') ||
                                     element.querySelector('.odd-value') ||
                                     element.querySelector('.koeff');
                        const odds = oddsEl ? parseFloat(oddsEl.textContent.replace(',', '').trim()) : 0.0;

                        // Extract stake
                        const stakeEl = element.querySelector('.stake') ||
                                      element.querySelector('.sum') ||
                                      element.querySelector('.bet-amount') ||
                                      element.querySelector('.bet-stake');
                        const stake = stakeEl ? parseFloat(stakeEl.textContent.replace(/[^\\d.-]/g, '').trim()) : 0.0;

                        // Extract status
                        const statusEl = element.querySelector('.status') ||
                                       element.querySelector('.bet-status') ||
                                       element.querySelector('.slip-status') ||
                                       element.querySelector('.result');
                        const status = statusEl ? statusEl.textContent.trim() : 'Unknown Status';

                        // Extract date if available
                        const dateEl = element.querySelector('.date') ||
                                     element.querySelector('.time') ||
                                     element.querySelector('.bet-date') ||
                                     element.querySelector('.created-date');
                        const date = dateEl ? dateEl.textContent.trim() : new Date().toISOString();

                        // Extract potential win if available
                        const potentialWinEl = element.querySelector('.potential-win') ||
                                              element.querySelector('.possible-win') ||
                                              element.querySelector('.max-payout');
                        const potentialWin = potentialWinEl ? parseFloat(potentialWinEl.textContent.replace(/[^\\d.-]/g, '').trim()) : 0.0;

                        // Extract actual win if available
                        const actualWinEl = element.querySelector('.actual-win') ||
                                           element.querySelector('.won-amount') ||
                                           element.querySelector('.payout');
                        const actualWin = actualWinEl ? parseFloat(actualWinEl.textContent.replace(/[^\\d.-]/g, '').trim()) : null;

                        bets.push({
                            match_name: matchName,
                            bet_type: betType,
                            odds: odds,
                            stake: stake,
                            status: status,
                            date: date,
                            potential_win: potentialWin,
                            actual_win: actualWin
                        });
                    } catch (error) {
                        console.warn('Error extracting bet data:', error);
                        continue; // Skip this element if there's an error
                    }
                }

                return bets;
            }
        """)

        return bets_data

    async def get_active_bets(self):
        """Get currently active/pending bets - READ ONLY"""
        # Navigate to active bets section
        await self.page.goto("https://1xbet.com/en/office/bets")

        # Wait for active bets to load
        await self.page.wait_for_selector('.active-bet, .current-bet, .live-bet', timeout=15000)

        active_bets = await self.page.evaluate("""
            () => {
                // Look for different possible selectors for active bets
                const betElements = document.querySelectorAll('.active-bet, .current-bet, .live-bet, .bet-slip');
                const bets = [];

                for (const element of betElements) {
                    try {
                        // Extract match name
                        const matchNameEl = element.querySelector('.match-name') ||
                                          element.querySelector('.event-name') ||
                                          element.querySelector('.team-name') ||
                                          element.querySelector('.participant');
                        const matchName = matchNameEl ? matchNameEl.textContent.trim() : 'Unknown Match';

                        // Extract bet type
                        const betTypeEl = element.querySelector('.bet-type') ||
                                        element.querySelector('.selection') ||
                                        element.querySelector('.bet-desc') ||
                                        element.querySelector('.outcome');
                        const betType = betTypeEl ? betTypeEl.textContent.trim() : 'Unknown Bet Type';

                        // Extract odds
                        const oddsEl = element.querySelector('.odds') ||
                                     element.querySelector('.coeff') ||
                                     element.querySelector('.odd-value');
                        const odds = oddsEl ? parseFloat(oddsEl.textContent.replace(',', '').trim()) : 0.0;

                        // Extract stake
                        const stakeEl = element.querySelector('.stake') ||
                                      element.querySelector('.sum') ||
                                      element.querySelector('.bet-amount');
                        const stake = stakeEl ? parseFloat(stakeEl.textContent.replace(/[^\\d.-]/g, '').trim()) : 0.0;

                        // Extract status
                        const statusEl = element.querySelector('.status') ||
                                       element.querySelector('.bet-status') ||
                                       element.querySelector('.slip-status');
                        const status = statusEl ? statusEl.textContent.trim() : 'Active';

                        // Extract potential win
                        const potentialWinEl = element.querySelector('.potential-win') ||
                                              element.querySelector('.possible-win') ||
                                              element.querySelector('.max-payout');
                        const potential_win = potentialWinEl ? parseFloat(potentialWinEl.textContent.replace(/[^\\d.-]/g, '').trim()) : 0.0;

                        // Extract remaining time if available
                        const timeLeftEl = element.querySelector('.time-left') ||
                                         element.querySelector('.remaining-time');
                        const time_left = timeLeftEl ? timeLeftEl.textContent.trim() : null;

                        bets.push({
                            match_name: matchName,
                            bet_type: betType,
                            odds: odds,
                            stake: stake,
                            status: status,
                            potential_win: potential_win,
                            time_left: time_left,
                            timestamp: new Date().toISOString()
                        });
                    } catch (error) {
                        console.warn('Error extracting active bet data:', error);
                        continue; // Skip this element if there's an error
                    }
                }

                return bets;
            }
        """)

        return active_bets

    async def ensure_read_only_mode(self):
        """Ensure we're in read-only mode by blocking dangerous actions"""
        # Block navigation to payment/deposit/withdrawal pages
        await self.page.route("**/*payment*", lambda route: route.abort())
        await self.page.route("**/*deposit*", lambda route: route.abort())
        await self.page.route("**/*withdraw*", lambda route: route.abort())
        await self.page.route("**/*cashout*", lambda route: route.abort())

        # Block clicks on dangerous elements
        await self.page.add_init_script("""
            // Disable click events on potentially dangerous elements
            document.addEventListener('click', function(e) {
                const target = e.target;
                const dangerousClasses = ['payment', 'deposit', 'withdraw', 'cashout', 'bet-place', 'place-bet'];

                for (const cls of dangerousClasses) {
                    if (target.classList.contains(cls) ||
                        target.closest(`.${cls}`) ||
                        target.tagName.toLowerCase() === 'form' &&
                        (target.action.includes(cls) || target.innerHTML.toLowerCase().includes(cls))) {
                        e.preventDefault();
                        e.stopPropagation();
                        console.warn('Blocked potentially dangerous action:', target);
                        return;
                    }
                }
            }, true);
        """)

    async def close(self):
        """Close the browser"""
        if self.browser:
            await self.browser.close()


# Example usage
async def main():
    scraper = BetScraper()
    try:
        # Initialize with headless=False to see the browser for debugging
        await scraper.initialize(headless=False)

        # Enable read-only mode
        await scraper.ensure_read_only_mode()

        # Login (credentials should come from secure storage)
        # await scraper.login("your_username", "your_password")

        # Navigate to history and scrape
        await scraper.navigate_to_history()
        bets = await scraper.scrape_bets()

        # Print results
        print(json.dumps(bets, indent=2))

    finally:
        await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())