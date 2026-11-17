//! Small deterministic PRNG, independent of platform and global mutable state.
//! No claim is made that sequences match Python's random/NumPy.
pub struct Rng { state: u64 }
impl Rng {
    pub fn new(seed: u64) -> Self {
        Self { state: if seed == 0 { 0x9e3779b97f4a7c15 } else { seed } }
    }
    pub fn next_u64(&mut self) -> u64 {
        self.state ^= self.state >> 12;
        self.state ^= self.state << 25;
        self.state ^= self.state >> 27;
        self.state.wrapping_mul(0x2545f4914f6cdd1d)
    }
    pub fn unit(&mut self) -> f64 { ((self.next_u64() >> 11) as f64) * (1.0 / 9007199254740992.0) }
    pub fn usize(&mut self, stop: usize) -> usize {
        assert!(stop > 0);
        ((self.next_u64() as u128 * stop as u128) >> 64) as usize
    }
    pub fn bool(&mut self, probability: f64) -> bool { self.unit() < probability }
    pub fn normal(&mut self) -> f64 {
        let u1 = (1.0 - self.unit()).max(f64::MIN_POSITIVE);
        let u2 = self.unit();
        (-2.0 * u1.ln()).sqrt() * (2.0 * std::f64::consts::PI * u2).cos()
    }
}
