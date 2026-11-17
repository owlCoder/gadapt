//! Exhaustive inspection for affordable finite stepped decision grids.
//! No absence certificate if any point was not validly evaluated.
use std::collections::HashSet;
use crate::model::Variable;

pub(crate) fn axes(vars:&[Variable], budget:usize)->Option<Vec<Vec<f64>>> {
    if vars.is_empty() || budget==0 {return None;}
    let budget=budget.min(100_000);
    let mut total=1usize;
    let mut result=Vec::new();
    for v in vars {
        let count=v.grid_len()?;
        total=total.checked_mul(count)?;
        if total>budget {return None;}
        let mut distinct=HashSet::new();
        let mut line=Vec::with_capacity(count);
        for i in 0..count {
            let x=v.grid_point(i)?;
            if !v.contains(x) || !distinct.insert(x.to_bits()) {return None;}
            line.push(x);
        }
        result.push(line);
    }
    Some(result)
}
pub(crate) fn point(axes:&[Vec<f64>],mut index:usize)->Vec<f64> {
    let mut values=vec![0.0;axes.len()];
    for i in (0..axes.len()).rev() {
        let n=axes[i].len();
        values[i]=axes[i][index%n];
        index/=n;
    }
    values
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test] fn binary_grid(){
        let vars=[Variable::new(0.0,1.0,Some(0.5)).unwrap()];
        let a=axes(&vars,3).unwrap();
        assert_eq!(a[0],vec![0.0,0.5,1.0]);
        assert_eq!(point(&a,2),vec![1.0]);
        assert!(axes(&vars,2).is_none());
    }
}
