/**
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.solr.handler.dataimport;

import org.junit.Assert;
import org.junit.Test;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;

/**
 * <p>
 * Test for VariableResolver
 * </p>
 *
 * @version $Id: TestVariableResolver.java 681182 2008-07-30 19:35:58Z shalin $
 * @since solr 1.3
 */
public class TestVariableResolver {

  @Test
  public void testSimpleNamespace() {
    VariableResolverImpl vri = new VariableResolverImpl();
    Map<String, Object> ns = new HashMap<String, Object>();
    ns.put("world", "WORLD");
    vri.addNamespace("hello", ns);
    Assert.assertEquals("WORLD", vri.resolve("hello.world"));
  }

  @Test
  public void testNestedNamespace() {
    VariableResolverImpl vri = new VariableResolverImpl();
    Map<String, Object> ns = new HashMap<String, Object>();
    ns.put("world", "WORLD");
    vri.addNamespace("hello", ns);
    ns = new HashMap<String, Object>();
    ns.put("world1", "WORLD1");
    vri.addNamespace("hello.my", ns);
    Assert.assertEquals("WORLD1", vri.resolve("hello.my.world1"));
  }

  @Test
  public void test3LevelNestedNamespace() {
    VariableResolverImpl vri = new VariableResolverImpl();
    Map<String, Object> ns = new HashMap<String, Object>();
    ns.put("world", "WORLD");
    vri.addNamespace("hello", ns);
    ns = new HashMap<String, Object>();
    ns.put("world1", "WORLD1");
    vri.addNamespace("hello.my.new", ns);
    Assert.assertEquals("WORLD1", vri.resolve("hello.my.new.world1"));
  }

  @Test
  public void dateNamespaceWithValue() {
    VariableResolverImpl vri = new VariableResolverImpl();
    HashMap<String, Evaluator> evaluators = new HashMap<String, Evaluator>();
    evaluators.put("formatDate", EvaluatorBag.getDateFormatEvaluator());
    vri.addNamespace("dataimporter.functions", EvaluatorBag
            .getFunctionsNamespace(vri, evaluators));
    Map<String, Object> ns = new HashMap<String, Object>();
    Date d = new Date();
    ns.put("dt", d);
    vri.addNamespace("A", ns);
    Assert
            .assertEquals(
                    new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(d),
                    vri
                            .replaceTokens("${dataimporter.functions.formatDate(A.dt,yyyy-MM-dd HH:mm:ss)}"));
  }

  @Test
  public void dateNamespaceWithExpr() {
    VariableResolverImpl vri = new VariableResolverImpl();
    HashMap<String, Evaluator> evaluators = new HashMap<String, Evaluator>();
    evaluators.put("formatDate", EvaluatorBag.getDateFormatEvaluator());
    vri.addNamespace("dataimporter.functions", EvaluatorBag
            .getFunctionsNamespace(vri, evaluators));
    String s = vri
            .replaceTokens("${dataimporter.functions.formatDate('NOW',yyyy-MM-dd HH:mm)}");
    Assert.assertEquals(new SimpleDateFormat("yyyy-MM-dd HH:mm")
            .format(new Date()), s);
  }

  @Test
  public void testDefaultNamespace() {
    VariableResolverImpl vri = new VariableResolverImpl();
    Map<String, Object> ns = new HashMap<String, Object>();
    ns.put("world", "WORLD");
    vri.addNamespace(null, ns);
    Assert.assertEquals("WORLD", vri.resolve("world"));
  }

  @Test
  public void testDefaultNamespace1() {
    VariableResolverImpl vri = new VariableResolverImpl();
    Map<String, Object> ns = new HashMap<String, Object>();
    ns.put("world", "WORLD");
    vri.addNamespace(null, ns);
    Assert.assertEquals("WORLD", vri.resolve("world"));
  }

  @Test
  public void testFunctionNamespace1() {
    final VariableResolverImpl resolver = new VariableResolverImpl();
    final Map<String, Evaluator> evaluators = new HashMap<String, Evaluator>();
    evaluators.put("formatDate", EvaluatorBag.getDateFormatEvaluator());
    evaluators.put("test", new Evaluator() {
      public String evaluate(VariableResolver resolver, String expression) {
        return "Hello World";
      }
    });

    resolver.addNamespace("dataimporter.functions", EvaluatorBag
            .getFunctionsNamespace(resolver, evaluators));
    String s = resolver
            .replaceTokens("${dataimporter.functions.formatDate('NOW',yyyy-MM-dd HH:mm)}");
    Assert.assertEquals(new SimpleDateFormat("yyyy-MM-dd HH:mm")
            .format(new Date()), s);
    Assert.assertEquals("Hello World", resolver
            .replaceTokens("${dataimporter.functions.test('TEST')}"));
  }
}
