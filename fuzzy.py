import numpy as np
import skfuzzy.control as ctrl
import skfuzzy as fuzz
import matplotlib.pyplot as plt

universe = np.linspace(0, 1, 21)

speed = ctrl.Antecedent(universe, 'speed')
gap = ctrl.Antecedent(universe, 'gap')
wall_dist = ctrl.Antecedent(universe, 'wall_dist')
booster = ctrl.Consequent(universe, 'booster')

gap['far_down'] = fuzz.trapmf(universe, [0, 0, 0.3, 0.4])
gap['near_down'] = fuzz.trapmf(universe, [0.35, 0.40, 0.45, 0.5])
gap['ahead'] = fuzz.trimf(universe, [0.45, 0.5, 0.55])
gap['near_up'] = fuzz.trapmf(universe, [0.5, 0.55, 0.6, 0.65])
gap['far_up'] = fuzz.trapmf(universe, [0.6, 0.7, 1, 1])

speed['fast_down'] = fuzz.trapmf(universe, [0, 0, 0.3, 0.4])
speed['slow_down'] = fuzz.trimf(universe, [0.3, 0.4, 0.5])
speed['none'] = fuzz.trimf(universe, [0.45, 0.5, 0.55])
speed['slow_up'] = fuzz.trimf(universe, [0.5, 0.6, 0.7])
speed['fast_up'] = fuzz.trapmf(universe, [0.6, 0.7, 1, 1])

wall_dist['safe'] = fuzz.trapmf(universe, [0.1, 0.4, 1, 1])
wall_dist['big'] = fuzz.trapmf(universe, [0.65, 0.8, 1, 1])
wall_dist['small'] = fuzz.trapmf(universe, [0, 0, 0.3, 0.5])

booster['off'] = fuzz.trapmf(universe, [0, 0, 0, 0.2])
booster['low'] = fuzz.trapmf(universe, [0., 0.2, 0.3, 0.35])
booster['shift_down'] = fuzz.trimf(universe, [0.15, 0.2, 0.25])
booster['medium'] = fuzz.trimf(universe, [0.4, 0.5, 0.6])
booster['shift_up'] = fuzz.trimf(universe, [0.75, 0.8, 0.85])
booster['high'] = fuzz.trapmf(universe, [0.65, 0.7, 0.8, 1])
booster['max'] = fuzz.trapmf(universe, [0.8, 1, 1, 1])


rules = [

    ctrl.Rule(antecedent=(gap['far_down'] & wall_dist['big']) |
                         (~gap['far_up'] & speed['fast_up']),
                  consequent=booster['off']),

    ctrl.Rule(antecedent=((gap['ahead'] | gap['near_down']) & speed['slow_up']) |
                         (gap['near_down'] & speed['none']) |
                         (gap['far_down'] & wall_dist['small']),
                  consequent=booster['low']),

    ctrl.Rule(antecedent=(gap['near_down'] & wall_dist['safe']),
                  consequent=booster['shift_down']),

    ctrl.Rule(antecedent=(gap['near_down'] & speed['slow_down']) |
                         (gap['ahead'] & speed['none']) |
                         (gap['near_up'] & speed['slow_up']),
                  consequent=booster['medium']),

    ctrl.Rule(antecedent=(gap['near_up'] & wall_dist['safe']),
                  consequent=booster['shift_up']),

    ctrl.Rule(antecedent=((gap['ahead'] | gap['near_up']) & speed['slow_down']) |
                         (gap['near_up'] & speed['none']) |
                         (gap['far_up'] & wall_dist['small']),
                  consequent=booster['high']),

    ctrl.Rule(antecedent=(gap['far_up'] & wall_dist['big']) |
                         (~gap['far_down'] & speed['fast_down']),
                  consequent=booster['max']),
]

system = ctrl.ControlSystem(rules=rules)

simulation = ctrl.ControlSystemSimulation(system)

def compute(speed, gap, wall_dist):
    inputs = {
        'speed': speed,
        'gap': gap,
        'wall_dist': wall_dist
    }

    simulation.inputs(inputs)
    simulation.compute()
    return simulation.output['booster']

if __name__ == '__main__':
    gap.view()
    speed.view()
    wall_dist.view()
    booster.view()
    plt.show()