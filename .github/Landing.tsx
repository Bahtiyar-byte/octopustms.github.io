import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  ChevronRight,
  DollarSign,
  Clock,
  Shield,
  Zap,
  Users,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Phone,
  Mail,
  Calendar,
  Truck,
  FileText,
  CreditCard,
  BarChart3,
  Target,
  Sparkles
} from 'lucide-react';

const Landing: React.FC = () => {
  const [loadsPerWeek, setLoadsPerWeek] = useState(50);
  const [timeToLaunch, setTimeToLaunch] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });

  // Countdown timer to October 24, 2025
  useEffect(() => {
    const calculateTimeLeft = () => {
      const launchDate = new Date('2025-10-24T00:00:00').getTime();
      const now = new Date().getTime();
      const difference = launchDate - now;

      if (difference > 0) {
        setTimeToLaunch({
          days: Math.floor(difference / (1000 * 60 * 60 * 24)),
          hours: Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
          minutes: Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60)),
          seconds: Math.floor((difference % (1000 * 60)) / 1000)
        });
      }
    };

    const timer = setInterval(calculateTimeLeft, 1000);
    return () => clearInterval(timer);
  }, []);

  const weeklyFee = loadsPerWeek * 20;
  const monthlyEstimate = weeklyFee * 4.33;
  const traditionalCost = 2000; // Average TMS cost
  const monthlySavings = Math.max(0, traditionalCost - monthlyEstimate);

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-green-600/20 animate-pulse" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24">
          {/* Launch Countdown Banner */}
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 rounded-full bg-green-500/10 border border-green-500/30 px-6 py-3 backdrop-blur-sm">
              <Sparkles className="w-5 h-5 text-green-400" />
              <span className="text-green-400 font-semibold">Revolution Launches October 24, 2025</span>
              <Sparkles className="w-5 h-5 text-green-400" />
            </div>
            <div className="flex justify-center gap-4 mt-4">
              {Object.entries(timeToLaunch).map(([unit, value]) => (
                <div key={unit} className="text-center">
                  <div className="text-3xl font-bold text-white">{value}</div>
                  <div className="text-xs text-gray-400 uppercase">{unit}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="text-center">
            <h1 className="text-5xl md:text-7xl font-black text-white mb-6 tracking-tight">
              Finally. A TMS that only
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-green-400 mt-2">
                wins when YOU win.
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-4 max-w-3xl mx-auto">
              Every other TMS charges you $500-5,000/month whether you book 1 load or 100.
              Whether you're profitable or bleeding money.
            </p>

            <p className="text-3xl font-bold text-white mb-8">
              We said <span className="text-red-400">"fuck that."</span>
            </p>

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 max-w-2xl mx-auto mb-12 border border-slate-700">
              <p className="text-4xl font-black text-white mb-4">
                $20 per booked load.
              </p>
              <p className="text-2xl text-green-400 font-bold">
                Zero loads = Zero cost.
              </p>
              <p className="text-lg text-gray-400 mt-4">
                Because software should be your partner, not your parasite.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register" className="group inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-slate-900 bg-gradient-to-r from-green-400 to-blue-400 rounded-xl hover:shadow-2xl hover:shadow-green-500/25 transition-all duration-200">
                Start Free - No Card Required
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <button className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white border-2 border-slate-600 rounded-xl hover:bg-slate-800 transition-colors">
                Watch 2-Min Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* The "FINALLY" Moment Section */}
      <section className="py-20 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
              "Finally, someone who GETS it!"
            </h2>
            <p className="text-xl text-gray-300">- Every dispatcher who sees Octopus</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
              <Clock className="w-12 h-12 text-blue-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">We know the 2 AM panic</h3>
              <p className="text-gray-400">When the broker calls asking "where's my load?" We've lived it.</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
              <FileText className="w-12 h-12 text-green-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">We know the Friday scramble</h3>
              <p className="text-gray-400">To get settlements done before everyone goes home. We've done it.</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
              <Zap className="w-12 h-12 text-red-400 mb-4" />
              <h3 className="text-xl font-bold text-white mb-2">We know the rage</h3>
              <p className="text-gray-400">When your TMS crashes during peak booking hours. We've felt it.</p>
            </div>
          </div>

          <p className="text-2xl font-bold text-center text-white mt-12">
            We built Octopus because we were YOU.
          </p>
        </div>
      </section>

      {/* Interactive LLMP Flow */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl md:text-5xl font-black text-center text-white mb-12">
            One-Click Magic
          </h2>

          <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-8 border border-slate-700">
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="flex-1 text-center">
                <div className="w-20 h-20 rounded-full bg-blue-500/20 border-2 border-blue-500 flex items-center justify-center mx-auto mb-4">
                  <Target className="w-10 h-10 text-blue-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Find</h3>
                <p className="text-sm text-gray-400 mt-2">Native DAT integration</p>
              </div>

              <ChevronRight className="w-8 h-8 text-gray-600 hidden md:block" />

              <div className="flex-1 text-center">
                <div className="w-20 h-20 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-10 h-10 text-green-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Book</h3>
                <p className="text-sm text-gray-400 mt-2">One click, done</p>
              </div>

              <ChevronRight className="w-8 h-8 text-gray-600 hidden md:block" />

              <div className="flex-1 text-center">
                <div className="w-20 h-20 rounded-full bg-purple-500/20 border-2 border-purple-500 flex items-center justify-center mx-auto mb-4">
                  <Truck className="w-10 h-10 text-purple-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Assign</h3>
                <p className="text-sm text-gray-400 mt-2">Auto-notify driver</p>
              </div>

              <ChevronRight className="w-8 h-8 text-gray-600 hidden md:block" />

              <div className="flex-1 text-center">
                <div className="w-20 h-20 rounded-full bg-yellow-500/20 border-2 border-yellow-500 flex items-center justify-center mx-auto mb-4">
                  <BarChart3 className="w-10 h-10 text-yellow-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Track</h3>
                <p className="text-sm text-gray-400 mt-2">Public tracking links</p>
              </div>

              <ChevronRight className="w-8 h-8 text-gray-600 hidden md:block" />

              <div className="flex-1 text-center">
                <div className="w-20 h-20 rounded-full bg-green-500/20 border-2 border-green-500 flex items-center justify-center mx-auto mb-4 animate-pulse">
                  <DollarSign className="w-10 h-10 text-green-400" />
                </div>
                <h3 className="text-lg font-bold text-white">Get Paid</h3>
                <p className="text-sm text-green-400 mt-2 font-bold">"Cashanggg!"</p>
              </div>
            </div>

            <div className="text-center mt-12">
              <p className="text-2xl font-bold text-white">
                What takes 47 clicks in other systems takes ONE in Octopus.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Partnership Calculator */}
      <section className="py-20 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              The Partnership Promise
            </h2>
            <p className="text-2xl text-green-400 font-bold">
              "We Don't Demand Money. We Demand BUSINESS!"
            </p>
          </div>

          <div className="bg-slate-900/50 rounded-2xl p-8 border border-slate-700">
            <div className="grid md:grid-cols-2 gap-8 mb-8">
              <div>
                <h3 className="text-xl font-bold text-red-400 mb-4">Traditional TMS:</h3>
                <p className="text-3xl font-black text-white">$2,000/month forever</p>
                <ul className="mt-4 space-y-2">
                  <li className="flex items-start text-gray-400">
                    <span className="text-red-400 mr-2">✗</span>
                    Pay even during slow weeks
                  </li>
                  <li className="flex items-start text-gray-400">
                    <span className="text-red-400 mr-2">✗</span>
                    Pay even if the software breaks
                  </li>
                  <li className="flex items-start text-gray-400">
                    <span className="text-red-400 mr-2">✗</span>
                    Locked into annual contracts
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="text-xl font-bold text-green-400 mb-4">Octopus:</h3>
                <p className="text-3xl font-black text-white">$20 only when you book</p>
                <ul className="mt-4 space-y-2">
                  <li className="flex items-start text-gray-300">
                    <span className="text-green-400 mr-2">✓</span>
                    Slow week with 10 loads? $200
                  </li>
                  <li className="flex items-start text-gray-300">
                    <span className="text-green-400 mr-2">✓</span>
                    Vacation week with 0 loads? $0
                  </li>
                  <li className="flex items-start text-gray-300">
                    <span className="text-green-400 mr-2">✓</span>
                    Boom week with 100 loads? Fair share
                  </li>
                </ul>
              </div>
            </div>

            <div className="border-t border-slate-700 pt-8">
              <h3 className="text-xl font-bold text-white mb-4">Calculate Your Savings</h3>
              <div className="flex items-center gap-4 mb-4">
                <label className="text-gray-300 flex-shrink-0">Loads per week:</label>
                <input
                  type="range"
                  min={0}
                  max={200}
                  value={loadsPerWeek}
                  onChange={(e) => setLoadsPerWeek(parseInt(e.target.value))}
                  className="flex-1 h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-2xl font-bold text-white w-16 text-right">{loadsPerWeek}</span>
              </div>

              <div className="grid md:grid-cols-4 gap-4">
                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-sm text-gray-400">Weekly with Octopus</p>
                  <p className="text-2xl font-bold text-white">${weeklyFee}</p>
                </div>
                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-sm text-gray-400">Monthly estimate</p>
                  <p className="text-2xl font-bold text-white">${Math.round(monthlyEstimate)}</p>
                </div>
                <div className="bg-slate-800 rounded-xl p-4">
                  <p className="text-sm text-gray-400">Traditional TMS</p>
                  <p className="text-2xl font-bold text-gray-500 line-through">${traditionalCost}</p>
                </div>
                <div className="bg-green-900/30 border border-green-500 rounded-xl p-4">
                  <p className="text-sm text-green-400">You save</p>
                  <p className="text-2xl font-bold text-green-400">${monthlySavings}/mo</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-black text-center text-white mb-12">
            Carriers Already Living the Revolution
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400 text-xl">★</span>
                ))}
              </div>
              <p className="text-gray-300 italic mb-4">
                "I don't care how much it costs, if it keeps all my shit together"
              </p>
              <p className="text-white font-bold">- Salim</p>
              <p className="text-gray-400 text-sm">15-truck fleet owner</p>
            </div>

            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400 text-xl">★</span>
                ))}
              </div>
              <p className="text-gray-300 italic mb-4">
                "My dispatcher literally dreams about this workflow"
              </p>
              <p className="text-white font-bold">- Marcus</p>
              <p className="text-gray-400 text-sm">Operations Manager</p>
            </div>

            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700">
              <div className="flex items-center mb-4">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className="text-yellow-400 text-xl">★</span>
                ))}
              </div>
              <p className="text-gray-300 italic mb-4">
                "First TMS that doesn't make me want to throw my computer out the window"
              </p>
              <p className="text-white font-bold">- Jennifer</p>
              <p className="text-gray-400 text-sm">Owner-Operator</p>
            </div>
          </div>

          <div className="flex justify-center gap-8 mt-12">
            <div className="text-center">
              <p className="text-4xl font-black text-green-400">10+</p>
              <p className="text-gray-400">Carriers already using</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-black text-blue-400">4hrs</p>
              <p className="text-gray-400">Saved per dispatcher/day</p>
            </div>
            <div className="text-center">
              <p className="text-4xl font-black text-purple-400">3x</p>
              <p className="text-gray-400">Faster settlements</p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust Architecture */}
      <section className="py-20 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-black text-white mb-4">
              Built By Truckers, For Truckers
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              We're not venture-funded bros trying to "disrupt" your industry.
              We're truckers who got tired of shitty software and built what we wished existed.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700 text-center">
              <Shield className="w-12 h-12 text-green-400 mx-auto mb-4" />
              <h3 className="font-bold text-white mb-2">No Contracts</h3>
              <p className="text-gray-400 text-sm">Cancel anytime (but nobody does)</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700 text-center">
              <Users className="w-12 h-12 text-blue-400 mx-auto mb-4" />
              <h3 className="font-bold text-white mb-2">No Setup Fees</h3>
              <p className="text-gray-400 text-sm">We're partners from day one</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700 text-center">
              <CreditCard className="w-12 h-12 text-purple-400 mx-auto mb-4" />
              <h3 className="font-bold text-white mb-2">No Hidden Costs</h3>
              <p className="text-gray-400 text-sm">Just $20 per booked load, forever</p>
            </div>
            <div className="bg-slate-900/50 rounded-xl p-6 border border-slate-700 text-center">
              <FileText className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
              <h3 className="font-bold text-white mb-2">No Data Hostage</h3>
              <p className="text-gray-400 text-sm">Export everything, anytime</p>
            </div>
          </div>

          <div className="mt-12 bg-gradient-to-r from-blue-900/30 to-green-900/30 rounded-2xl p-8 border border-blue-500/30">
            <h3 className="text-2xl font-bold text-white mb-4 text-center">The Dream Squad</h3>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
              <div>
                <div className="text-3xl mb-2">🐙</div>
                <p className="text-white font-bold">Octopus</p>
                <p className="text-gray-400 text-xs">Orchestration</p>
              </div>
              <div>
                <div className="text-3xl mb-2">💳</div>
                <p className="text-white font-bold">Stripe</p>
                <p className="text-gray-400 text-xs">Settlements</p>
              </div>
              <div>
                <div className="text-3xl mb-2">📊</div>
                <p className="text-white font-bold">DAT</p>
                <p className="text-gray-400 text-xs">Load Board</p>
              </div>
              <div>
                <div className="text-3xl mb-2">☁️</div>
                <p className="text-white font-bold">AWS</p>
                <p className="text-gray-400 text-xs">Infrastructure</p>
              </div>
              <div>
                <div className="text-3xl mb-2">🤖</div>
                <p className="text-white font-bold">Claude</p>
                <p className="text-gray-400 text-xs">Intelligence</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-3xl p-12 text-center">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              Stop Accepting Broken.
            </h2>
            <p className="text-xl text-white/90 mb-8 max-w-3xl mx-auto">
              You move America. You deserve tools that respect your intelligence,
              value your time, and share your success.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/register" className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-blue-900 bg-white rounded-xl hover:shadow-2xl transition-all duration-200">
                Start Free Now
                <ArrowRight className="ml-2 w-5 h-5" />
              </Link>
              <button className="inline-flex items-center justify-center px-8 py-4 text-lg font-bold text-white border-2 border-white/50 rounded-xl hover:bg-white/10 transition-colors">
                <Phone className="mr-2 w-5 h-5" />
                Book Quick Demo
              </button>
            </div>

            <p className="text-white/70 mt-6">
              Or call us: <span className="text-white font-bold">1-800-OCTOPUS</span>
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <img src="/octopus-logo.svg" alt="Octopus" className="h-16 mx-auto mb-4" />
            <p className="text-2xl font-bold text-white mb-2">
              "We lived the pain. We built the cure. Now we share the success."
            </p>
            <p className="text-gray-400 mb-4">
              Octopus TMS - Where partnership replaces subscription.
            </p>
            <p className="text-green-400 font-bold text-xl">
              Coming October 24, 2025. The revolution has tentacles. 🐙
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 mt-12 pt-8 border-t border-slate-800">
            <div>
              <h3 className="text-white font-bold mb-4">Product</h3>
              <ul className="space-y-2">
                <li><a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                <li><a href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#demo" className="text-gray-400 hover:text-white transition-colors">Demo</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-bold mb-4">Company</h3>
              <ul className="space-y-2">
                <li><a href="#about" className="text-gray-400 hover:text-white transition-colors">About</a></li>
                <li><a href="#contact" className="text-gray-400 hover:text-white transition-colors">Contact</a></li>
                <li><a href="#careers" className="text-gray-400 hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-bold mb-4">Resources</h3>
              <ul className="space-y-2">
                <li><a href="#blog" className="text-gray-400 hover:text-white transition-colors">Blog</a></li>
                <li><a href="#help" className="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#api" className="text-gray-400 hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-bold mb-4">Connect</h3>
              <div className="flex gap-4">
                <Mail className="w-6 h-6 text-gray-400 hover:text-white cursor-pointer transition-colors" />
                <Phone className="w-6 h-6 text-gray-400 hover:text-white cursor-pointer transition-colors" />
                <Calendar className="w-6 h-6 text-gray-400 hover:text-white cursor-pointer transition-colors" />
              </div>
            </div>
          </div>

          <div className="mt-8 pt-8 border-t border-slate-800 text-center text-gray-400 text-sm">
            <p>© 2025 Octopus TMS. Built with ❤️ by ex-trucker who codes.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Landing;