use crate::model::{Candidate, DiversityMetric, Variable};

pub(crate) fn spread(values: &[f64], metric: DiversityMetric) -> f64 {
    if values.len() < 2 { return 0.0; }
    let min = values.iter().copied().fold(f64::INFINITY, f64::min);
    let max = values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    if min == max { return 0.0; }
    let scaled: Vec<f64> = values.iter().map(|&v| {
        match metric {
            DiversityMetric::Linear | DiversityMetric::AffineInvariant => {
                let span = max - min;
                if span.is_finite() { ((v - min) / span).clamp(0.0, 1.0) }
                else {
                    ((v * 0.5 - min * 0.5) / (max * 0.5 - min * 0.5)).clamp(0.0, 1.0)
                }
            }
            DiversityMetric::LogRelative => {
                let gap = v - min;
                if gap.is_finite() { gap.max(0.0).ln_1p() }
                else { (-min).ln() + (v / -min).ln_1p() }
            }
        }
    }).collect();
    let mean = scaled.iter().sum::<f64>() / scaled.len() as f64;
    let variance = scaled.iter().map(|v| (v-mean)*(v-mean)).sum::<f64>() / (scaled.len()-1) as f64;
    variance.sqrt()
}
pub(crate) fn relative(current: f64, baseline: &mut Option<f64>) -> f64 {
    if !current.is_finite() || current <= 0.0 { return 0.0; }
    match baseline {
        None => { *baseline = Some(current); 1.0 }
        Some(b) if *b > 0.0 => (current / *b).clamp(0.0, 1.0),
        Some(_) => 1.0,
    }
}
pub(crate) fn cost(population: &[Candidate], metric: DiversityMetric, baseline: &mut Option<f64>) -> f64 {
    let values: Vec<_> = population.iter().filter(|c| c.valid && c.score.is_finite())
        .map(|c| c.score).collect();
    relative(spread(&values, metric), baseline)
}
pub(crate) fn columns(population: &[Candidate], vars: &[Variable], metric: DiversityMetric,
    baselines: &mut [Option<f64>]) -> Vec<f64> {
    (0..vars.len()).map(|column| {
        let v: Vec<_> = population.iter().filter(|c| c.valid).map(|c| c.values[column]).collect();
        match metric {
            DiversityMetric::Linear | DiversityMetric::AffineInvariant => {
                let min = vars[column].min;
                let max = vars[column].max;
                let span = max - min;
                let normalized: Vec<_> = v.iter().map(|x| {
                    if span.is_finite() { (x-min)/span }
                    else { (x*0.5 - min*0.5)/(max*0.5 - min*0.5) }
                }).collect();
                relative(stddev(&normalized), &mut baselines[column])
            }
            DiversityMetric::LogRelative => {
                let min = vars[column].min;
                let logged: Vec<_> = v.iter().map(|x| {
                    let gap = x - min;
                    if gap.is_finite() { gap.max(0.0).ln_1p() }
                    else { (-min).ln() + (x / -min).ln_1p() }
                }).collect();
                relative(stddev(&logged), &mut baselines[column])
            }
        }
    }).collect()
}
fn stddev(values: &[f64]) -> f64 {
    if values.len() < 2 { return 0.0; }
    let base = values[0];
    let translated: Vec<_> = values.iter().map(|v| v-base).collect();
    let m = translated.iter().sum::<f64>() / translated.len() as f64;
    (translated.iter().map(|v| (v-m)*(v-m)).sum::<f64>() / (translated.len()-1) as f64).sqrt()
}
pub(crate) fn parent_distance(a: &[f64], b: &[f64], vars: &[Variable]) -> f64 {
    if vars.is_empty() { return 0.0; }
    let result: f64 = a.iter().zip(b).zip(vars).map(|((&x,&y), v)| {
        let span=v.max-v.min;
        if span.is_finite() { ((x-y)/span).abs() }
        else { ((x*0.5-y*0.5)/(v.max*0.5-v.min*0.5)).abs() }
    }).sum();
    (result / vars.len() as f64).clamp(0.0,1.0)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn zero_spread(){assert_eq!(spread(&[1.0,1.0],DiversityMetric::LogRelative),0.0);}
    #[test] fn extremes(){
        let a = spread(&[-1e308,1e308],DiversityMetric::AffineInvariant);
        assert!(a.is_finite() && a>0.0);
    }
}
