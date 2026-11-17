use crate::model::{Candidate, Crossover, Mutation, Options, ParentSelection, Variable};
use crate::rng::Rng;

pub(crate) fn sample(variable: &Variable, rng: &mut Rng) -> f64 {
    // Sampling by a uniform grid index avoids the half-weighted endpoints
    // created by sampling a continuous value and snapping to the nearest point.
    if let Some(n)=variable.grid_len(){
        return variable.grid_point(rng.usize(n)).unwrap_or(variable.min);
    }
    let u=rng.unit();
    (variable.min*(1.0-u)+variable.max*u).clamp(variable.min,variable.max)
}
pub(crate) fn snap(value:f64, variable:&Variable)->f64 {
    let x=value.clamp(variable.min,variable.max);
    let Some(n)=variable.grid_len() else{return x;};
    let step=variable.step.unwrap();
    let i=((x-variable.min)/step).round().clamp(0.0,(n-1) as f64) as usize;
    variable.grid_point(i).unwrap_or(x)
}
pub(crate) fn parent_index(elites:&[Candidate], method:ParentSelection,rng:&mut Rng)->usize {
    let n=elites.len();
    match method {
        ParentSelection::Random=>rng.usize(n),
        ParentSelection::TopToBottom=>{
            // A bias toward top-ranked candidates, without making lower ranks unreachable.
            let x=rng.unit();
            ((x*x*n as f64).floor() as usize).min(n-1)
        }
        ParentSelection::Tournament(k)=>{
            let mut best=rng.usize(n);
            for _ in 1..k.max(1) {
                let j=rng.usize(n);
                if j<best{best=j;}
            }
            best
        }
        ParentSelection::Roulette=>{
            let total=(n*(n+1)/2) as f64;
            let draw=rng.unit()*total;
            let mut acc=0.0;
            for idx in 0..n {
                acc+=(n-idx) as f64;
                if draw<acc{return idx;}
            }
            n-1
        }
    }
}
fn lerp(a:f64,b:f64,t:f64)->f64 {
    let v = a*(1.0-t)+b*t;
    if v.is_finite(){v}else{a*0.5+b*0.5}
}
pub(crate) fn cross(
    first:&Candidate, second:&Candidate, third:&Candidate,
    vars:&[Variable], options:&Options, prob:f64, rng:&mut Rng
)->Vec<f64>{
    first.values.iter().zip(&second.values).zip(&third.values).zip(vars)
        .map(|(((&a,&b),&c),var)|{
            if !rng.bool(prob){ return a; }
            let result=match options.crossover {
                Crossover::Uniform=>if rng.bool(0.5){a}else{b},
                Crossover::Blending=>{
                    // Blend with limited extrapolation for exploration.
                    let alpha=rng.unit()*1.5-0.25;
                    lerp(a,b,alpha)
                }
                Crossover::Differential=>{
                    // Correctly handles even large finite endpoints by scaling differences first.
                    let delta=(b*0.5-c*0.5)*rng.unit();
                    a+delta
                }
            };
            snap(if result.is_finite(){result}else{a},var)
        }).collect()
}
pub(crate) fn mutate(
    values:&mut [f64], vars:&[Variable], options:&Options, columns:&[f64],
    force:bool, rng:&mut Rng, stagnant_generations:usize
)->usize {
    let dims=values.len();
    if dims==0{return 0;}
    let avg=columns.iter().sum::<f64>()/dims as f64;
    let mut cap=options.max_mutated_variables.unwrap_or_else(||{
        (dims as f64*options.decision_variable_mutation_fraction).round() as usize
    }).clamp(1,dims);
    if !options.strict_mutation_decision_variable_limit {
        cap=cap.max((dims+4)/5).min(dims);
    }
    let focused=options.mutation_focus_generations.is_some()
        && !rng.bool(options.mutation_focus_exploration_probability);
    let focus=if focused {
        0.5f64.powf(stagnant_generations as f64/options.mutation_focus_generations.unwrap())
    }else{1.0};
    let mut desired=if force {1+rng.usize(cap)}else{
        (1.0+rng.unit()*(cap as f64)*(0.25+0.75*avg)).floor() as usize
    }.clamp(1,cap);
    desired=((desired as f64*focus).ceil() as usize).clamp(1,cap);
    let mut candidates:Vec<usize>=(0..dims).collect();
    let mut changed=0;
    for _ in 0..desired {
        if candidates.is_empty(){break;}
        let weights:Vec<f64>=candidates.iter().map(|&i| (1.0-columns[i]).max(0.001)).collect();
        let sum=weights.iter().sum::<f64>();
        let mut target=rng.unit()*sum;
        let mut pick=candidates.len()-1;
        for (i,w) in weights.iter().enumerate(){
            target-=w;
            if target<=0.0{pick=i;break;}
        }
        let i=candidates.swap_remove(pick);
        let old=values[i];
        let var=&vars[i];
        let selected=match options.mutation {
            Mutation::Mixed=>if rng.bool(0.5*focus){Mutation::Random}else{Mutation::Normal},
            other=>other
        };
        let next=match selected {
            Mutation::Random=>sample(var,rng),
            Mutation::ExtremePointed=>if rng.bool(0.5){var.min}else{var.max},
            Mutation::Normal | Mutation::Mixed => {
                let decay=options.min_std_dev_decay_generations.map(|n|{
                    0.1f64.powf(stagnant_generations as f64/n.max(1) as f64)
                }).unwrap_or(1.0);
                let step_floor=var.step.and_then(|s|{
                    let span=var.max-var.min;
                    if span.is_finite() && span>0.0 {Some(s/span)}else{None}
                }).unwrap_or(0.0);
                let min_std=(options.normal_mutation_min_std_dev*decay)
                    .max(1e-9).max(step_floor);
                let std=min_std+
                    (options.normal_mutation_max_std_dev-min_std)*columns[i].clamp(0.0,1.0);
                // Calculate in normalized space to avoid infinite ranges.
                let normalized=if (var.max-var.min).is_finite(){
                    (old-var.min)/(var.max-var.min)
                }else{
                    (old*0.5-var.min*0.5)/(var.max*0.5-var.min*0.5)
                };
                let u=(normalized+rng.normal()*std).clamp(0.0,1.0);
                let raw=lerp(var.min,var.max,u);
                snap(raw,var)
            }
        };
        if next!=old {values[i]=next; changed+=1;}
    }
    // An explicitly forced mutation must try to escape identical parents.
    if force && changed==0 {
        let i=rng.usize(dims);
        for _ in 0..8 {
            let candidate=sample(&vars[i],rng);
            if candidate!=values[i] {values[i]=candidate;changed+=1;break;}
        }
    }
    changed
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn uniform_respects_bounds(){
        let var=Variable::new(-1e308,1e308,None).unwrap();
        let mut rng=Rng::new(3);
        for _ in 0..1000 {let x=sample(&var,&mut rng);assert!(x>=var.min&&x<=var.max&&x.is_finite());}
    }
}
