//! Correlation-guided compensatory mutation, estimated once per generation.
use crate::model::{Candidate, CompensatoryMode, Variable};
use crate::operators::snap;
use crate::rng::Rng;

fn norm(x:f64,v:&Variable)->f64{
    let s=v.max-v.min;
    if s.is_finite(){((x-v.min)/s).clamp(0.0,1.0)}
    else{((x*0.5-v.min*0.5)/(v.max*0.5-v.min*0.5)).clamp(0.0,1.0)}
}
fn denorm(x:f64,v:&Variable)->f64{
    v.min*(1.0-x)+v.max*x
}
fn cov(rows:&[Vec<f64>],i:usize,j:usize)->f64 {
    if rows.len()<2{return 0.0;}
    let n=rows.len() as f64;
    let mean_i=rows.iter().map(|r|r[i]).sum::<f64>()/n;
    let mean_j=rows.iter().map(|r|r[j]).sum::<f64>()/n;
    rows.iter().map(|r|(r[i]-mean_i)*(r[j]-mean_j)).sum::<f64>()/(n-1.0)
}
fn rho(rows:&[Vec<f64>],i:usize,j:usize)->f64 {
    let s=(cov(rows,i,i)*cov(rows,j,j)).sqrt();
    if s<=1e-12{0.0}else{(cov(rows,i,j)/s).clamp(-1.0,1.0)}
}
pub(crate) struct Linkage {
    mode:CompensatoryMode,
    means:Vec<f64>,covariance:Vec<Vec<f64>>,correlation:Vec<Vec<f64>>,allowed:Vec<Vec<bool>>,
}
impl Linkage {
    pub fn build(elites:&[Candidate],vars:&[Variable],mode:CompensatoryMode)->Option<Self>{
        let d=vars.len();
        // Bound O(d^2) auxiliary memory on large-dimensional problems.
        if d<2 || d>256 || elites.len()<d+2{return None;}
        let rows:Vec<Vec<f64>>=elites.iter().filter(|c|c.valid).map(|c|{
            c.values.iter().zip(vars).map(|(&x,v)|norm(x,v)).collect()
        }).collect();
        if rows.len()<d+2{return None;}
        let means=(0..d).map(|i|rows.iter().map(|r|r[i]).sum::<f64>()/rows.len() as f64)
            .collect();
        let mut covariance=vec![vec![0.0;d];d];
        let mut correlation=vec![vec![0.0;d];d];
        for i in 0..d {
            covariance[i][i]=cov(&rows,i,i);
            for j in 0..i {
                let c=cov(&rows,i,j);
                covariance[i][j]=c;
                covariance[j][i]=c;
            }
        }
        for i in 0..d {
            for j in 0..i {
                let s=(covariance[i][i]*covariance[j][j]).sqrt();
                let r=if s>1e-12{(covariance[i][j]/s).clamp(-1.0,1.0)}else{0.0};
                correlation[i][j]=r;correlation[j][i]=r;
            }
        }
        let mut allowed=vec![vec![true;d];d];
        for i in 0..d{allowed[i][i]=false;}
        if mode==CompensatoryMode::Gated {
            let a:Vec<_>=rows.iter().step_by(2).cloned().collect();
            let b:Vec<_>=rows.iter().skip(1).step_by(2).cloned().collect();
            if a.len()<3 || b.len()<3{return None;}
            for i in 0..d {
                for j in 0..i {
                    let x=rho(&a,i,j);let y=rho(&b,i,j);
                    let accepted=x.abs()>=0.5&&y.abs()>=0.5&&x.signum()==y.signum();
                    allowed[i][j]=accepted;allowed[j][i]=accepted;
                }
            }
        }
        Some(Self{mode,means,covariance,correlation,allowed})
    }
    pub fn apply(&self,values:&mut[f64],before:&[f64],vars:&[Variable],rng:&mut Rng){
        let d=vars.len();
        let mut changed:Vec<_>=(0..d).filter(|&i|values[i]!=before[i]).collect();
        let mut used=vec![false;d];
        for &i in &changed{used[i]=true;}
        for k in (1..changed.len()).rev(){let j=rng.usize(k+1);changed.swap(j,k);}
        for i in changed {
            let mut best=None;let mut max_rho=0.0;
            for j in 0..d {
                let r=self.correlation[i][j].abs();
                if !used[j]&&self.allowed[i][j]&&r>max_rho {
                    max_rho=r;best=Some(j);
                }
            }
            let Some(j)=best else {continue;};
            let partner=if self.mode==CompensatoryMode::Permuted {
                let free_count=used.iter().filter(|&&taken|!taken).count();
                let chosen=rng.usize(free_count);
                (0..d).filter(|&x|!used[x]).nth(chosen).unwrap()
            }else{j};
            let slope=self.covariance[j][i]/(self.covariance[i][i]+1e-12);
            let new_x=if self.mode==CompensatoryMode::Resample {
                let diff=norm(values[i],&vars[i])-self.means[i];
                let variance=(self.covariance[j][j]-
                    self.covariance[j][i].powi(2)/(self.covariance[i][i]+1e-12)).max(0.0);
                self.means[j]+slope*diff+variance.sqrt()*rng.normal()
            } else {
                norm(values[partner],&vars[partner])+slope.clamp(-2.0,2.0)*
                    (norm(values[i],&vars[i])-norm(before[i],&vars[i]))
            };
            if new_x.is_finite(){
                let folded=new_x.rem_euclid(2.0);
                let reflected=if folded<=1.0{folded}else{2.0-folded};
                values[partner]=snap(denorm(reflected,&vars[partner]),&vars[partner]);
            }
            used[partner]=true;
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]fn gated_correlation_tracks_a_partner(){
        let vars=vec![Variable::new(0.0,1.0,None).unwrap();2];
        let elites:Vec<_>=(0..8).map(|i|{
            let x=i as f64/10.0;
            let mut c=Candidate::new(vec![x,x]);c.valid=true;c
        }).collect();
        let model=Linkage::build(&elites,&vars,CompensatoryMode::Gated).unwrap();
        let mut values=[0.7,0.4];
        model.apply(&mut values,&[0.4,0.4],&vars,&mut Rng::new(7));
        assert!(values[1]>0.4 && values[1]<=1.0);
    }
}
