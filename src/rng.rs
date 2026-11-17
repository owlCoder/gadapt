//! Small deterministic PRNG, independent of platform and global mutable state.
//! No claim is made that sequences match Python's random/NumPy.
pub struct Rng { state: u64, normal_spare:Option<f64> }
impl Rng {
    pub fn new(seed: u64) -> Self {
        Self { state: if seed == 0 { 0x9e3779b97f4a7c15 } else { seed },
            normal_spare:None }
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
        if let Some(spare)=self.normal_spare.take(){return spare;}
        let u1=(1.0-self.unit()).max(f64::MIN_POSITIVE);
        let theta=2.0*std::f64::consts::PI*self.unit();
        let radius=(-2.0*u1.ln()).sqrt();
        let (sin,cos)=theta.sin_cos();
        self.normal_spare=Some(radius*sin);
        radius*cos
    }
}

#[cfg(test)]
mod tests{
    use super::*;
    #[test]fn seeded_normal_stream_is_finite_and_reproducible(){
        let mut a=Rng::new(17);let mut b=Rng::new(17);
        for _ in 0..5000 {
            let x=a.normal();let y=b.normal();
            assert!(x.is_finite());assert_eq!(x,y);
        }
    }
}
