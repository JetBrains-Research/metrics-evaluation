import random
from sacrebleu_code.sacrebleu_methods.compat import corpus_bleu
from numpy import mean
import json


def synthesize_model(
    model_dictionary, base_model, other_models, change_percentage, metrics, improve=True
):
    model_size = len(model_dictionary)
    change_lump = round(change_percentage * model_size / 100)
    new_model = base_model + "_" + str(change_percentage) + "_" + str(int(improve))
    changes_list = []
    for i in range(model_size):
        changed = False
        change = (0, i, "model")
        for model in other_models:
            diff = (
                model_dictionary[i]["grade-" + model]
                - model_dictionary[i]["grade-" + base_model]
            )
            improved_when_needed = (improve is True) and (diff > 0)
            worsened_when_needed = (improve is False) and (diff < 0)
            if improved_when_needed or worsened_when_needed:
                if change[0] < abs(diff):
                    change = (abs(diff), i, model)
                changed = True
        if changed is True:
            changes_list.append(change)
    changes_list.sort(key=lambda tup: tup[0], reverse=True)
    changes_list = changes_list[:change_lump]
    change_lump -= len(changes_list)
    for item in changes_list:
        i = item[1]
        model = item[2]
        model_dictionary[i]["grade-" + new_model] = model_dictionary[i][
            "grade-" + model
        ]
        model_dictionary[i][new_model] = model_dictionary[i][model]
        for metric in metrics:
            model_dictionary[i][metric + "-" + new_model] = model_dictionary[i][
                metric + "-" + model
            ]

    for item in model_dictionary:
        item["grade-" + new_model] = item.get(
            "grade-" + new_model, item["grade-" + base_model]
        )
        item[new_model] = item.get(new_model, item[base_model])
        for metric in metrics:
            item[metric + "-" + new_model] = item.get(
                metric + "-" + new_model, item[metric + "-" + base_model]
            )
    if change_lump > 0:
        print(
            f"Failed to generate enough changed snippets. {change_lump} new snippets are lacking."
        )


def bootstrapped_bleu(model_dictionary, model_name, bootstrap_list):
    hyp = []
    ref = [[]]
    for i in bootstrap_list:
        hyp.append(model_dictionary[i][model_name])
        ref[0].append((model_dictionary[i]["snippet"]))
    return corpus_bleu(hyp, ref, tokenize="code")


def bootstrapped_metric(model_dictionary, model_name, metric, bootstrap_indices):
    scores = []
    grade_name = metric + "-" + model_name
    for i in bootstrap_indices:
        scores.append(model_dictionary[i][grade_name])
    return mean(scores)


def compare_models(model1, model2):
    m1 = 0
    for item1, item2 in zip(model1, model2):
        if item1 > item2:
            m1 += 1
    return m1 / len(model1)


def bootstrap(model_dictionary, models, metrics, p_value=0.05, bootstrap_sampling=500):
    model_size = len(model_dictionary)
    model_scores = dict()
    model_pairs = dict()
    bootstrap_results = dict()
    for model in models:
        model_scores[model] = dict()
        bootstrap_results[model] = dict()
        for metric in metrics:
            bootstrap_results[model][metric] = []
    for i in range(bootstrap_sampling):
        bootstrap_list = random.choices([m for m in range(model_size)], k=model_size)
        print(bootstrap_list)
        for m, model in enumerate(models):
            for metric in metrics:
                if metric == "bleu":
                    bootstrap_results[model][metric].append(
                        bootstrapped_bleu(model_dictionary, model, bootstrap_list)
                    )
                else:
                    bootstrap_results[model][metric].append(
                        bootstrapped_metric(
                            model_dictionary, model, metric, bootstrap_list
                        )
                    )

    for model1 in models:
        model_pairs[model1] = dict()
        for model2 in models:
            model_pairs[model1][model2] = dict()
            for metric in metrics:
                model_pairs[model1][model2][metric] = compare_models(
                    bootstrap_results[model1][metric], bootstrap_results[model2][metric]
                )

    for model in models:
        for metric in metrics:
            bootstrap_results[model][metric].sort()
            print(model, metric)
            print(bootstrap_results[model][metric])
            model_scores[model][metric + "-low"] = bootstrap_results[model][metric][
                round(p_value * bootstrap_sampling / 2)
            ]
            model_scores[model][metric + "-high"] = bootstrap_results[model][metric][
                -round(p_value * bootstrap_sampling / 2)
            ]

    return model_pairs, model_scores


def kendall_tau_metric(model_dictionary, models, metric):
    concordant_pairs = 0
    discordant_pairs = 0
    for model in models:
        for i, snippet1 in enumerate(model_dictionary[model]):
            for j, snippet2 in enumerate(model_dictionary[model]):
                if i > j:
                    if snippet1["gold-" + model] == snippet2["gold-" + model]:
                        continue
                    elif (snippet1["gold-" + model] > snippet2["gold-" + model]) and (
                        snippet1["grade-" + model + "-" + metric]
                        > snippet2["grade-" + model + "-" + metric]
                    ):
                        concordant_pairs += 1
                    elif (snippet1["gold-" + model] < snippet2["gold-" + model]) and (
                        snippet1["grade-" + model + "-" + metric]
                        < snippet2["grade-" + model + "-" + metric]
                    ):
                        concordant_pairs += 1
                    else:
                        discordant_pairs += 1
    kendall_tau = (concordant_pairs - discordant_pairs) / (
        concordant_pairs + discordant_pairs
    )
    return kendall_tau


def kendall_tau_people(
    model_dictionary, models, grader1, grader2
):  # how should we properly write that?
    concordant_pairs = 0
    discordant_pairs = 0
    for model in models:
        grader_1 = grader1 + "-" + model
        grader_2 = grader2 + "-" + model
        for i, snippet1 in enumerate(model_dictionary[model]):
            for j, snippet2 in enumerate(model_dictionary[model]):
                if i > j:
                    if (
                        (snippet1.get(grader_1) is None)
                        or (snippet2.get(grader_1) is None)
                        or (snippet1.get(grader_1) is None)
                        or (snippet2.get(grader_1) is None)
                    ):
                        continue
                    if (snippet1[grader_2] == snippet2[grader_2]) and (
                        snippet1[grader_1] == snippet2[grader_1]
                    ):
                        concordant_pairs += 1
                    elif (snippet1[grader_2] > snippet2[grader_2]) and (
                        snippet1[grader_1] > snippet2[grader_1]
                    ):
                        concordant_pairs += 1
                    elif (snippet1[grader_2] < snippet2[grader_2]) and (
                        snippet1[grader_1] < snippet2[grader_1]
                    ):
                        concordant_pairs += 1
                    else:
                        discordant_pairs += 1
    kendall_tau = (concordant_pairs - discordant_pairs) / (
        concordant_pairs + discordant_pairs
    )
    return kendall_tau


def main():
    model_dictionary = json.load(open("./to-grade/all-singles.json"))
    lst = [i for i in range(len(model_dictionary) - 225)]
    a = bootstrapped_bleu(model_dictionary, "tranx-annot", lst)
    print(a)


if __name__ == "__main__":
    main()
